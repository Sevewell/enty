from flask import Flask, render_template, redirect, url_for, session, flash, request
from authlib.integrations.flask_client import OAuth
import os
from datetime import datetime, date
from dotenv import load_dotenv
from db import (
    EntityMetaRepository, 
    EntityRepository, 
    AttributeRepository, 
    AttributeMetaRepository
)

# 環境変数を読み込み
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# OAuth設定
oauth = OAuth(app)

# 単一OIDCプロバイダー設定
METADATA_URL = os.environ.get('OIDC_METADATA_URL')
CLIENT_ID = os.environ.get('OIDC_CLIENT_ID')
CLIENT_SECRET = os.environ.get('OIDC_CLIENT_SECRET')
SCOPE = os.environ.get('OIDC_SCOPE', 'openid profile email')
PROVIDER_NAME = os.environ.get('OIDC_PROVIDER_NAME', 'OIDC Provider')

# 設定チェック
if not all([METADATA_URL, CLIENT_ID, CLIENT_SECRET]):
    raise ValueError("OIDC_METADATA_URL, OIDC_CLIENT_ID, OIDC_CLIENT_SECRET are required")

# OIDCクライアント登録
oidc = oauth.register(
    'oidc',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=METADATA_URL,
    client_kwargs={'scope': SCOPE},
)

# ホームページ
@app.route('/')
def index():
    user = session.get('user')
    view_date = get_view_date()
    return render_template('index.html', user=user, view_date=view_date, provider_name=PROVIDER_NAME)

# ログイン開始
@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    print(f"Redirect URI: {redirect_uri}")
    return oidc.authorize_redirect(redirect_uri)

# 認証コールバック
@app.route('/authorize')
def authorize():
    try:
        token = oidc.authorize_access_token()
        
        if token:
            userinfo = get_user_info(token)
            
            if userinfo:
                session['user'] = userinfo
                flash(f'{PROVIDER_NAME}でのログインに成功しました！', 'success')
                return redirect(url_for('profile'))
            else:
                flash('ユーザー情報の取得に失敗しました', 'error')
                return redirect(url_for('index'))
        else:
            flash('認証に失敗しました', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'認証エラー: {str(e)}', 'error')
        return redirect(url_for('index'))

def get_user_info(token):
    """OIDC標準のユーザー情報取得"""
    try:
        userinfo = token.get('userinfo')
        if userinfo:
            print(f"UserInfo received: {userinfo}")
            return {
                'id': userinfo.get('sub'),
                'name': userinfo.get('name') or userinfo.get('preferred_username'),
                'email': userinfo.get('email'),
                'picture': userinfo.get('picture'),
                'cipher_key': userinfo.get('cipher_key')
            }
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None
    
    return None

# プロフィールページ
@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        flash('ログインが必要です', 'warning')
        return redirect(url_for('index'))
    
    return render_template('profile.html', user=user, provider_name=PROVIDER_NAME)

# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    flash(f'{PROVIDER_NAME}からログアウトしました', 'info')
    return redirect(url_for('index'))

# 認証が必要なページの例
@app.route('/protected')
def protected():
    user = session.get('user')
    if not user:
        flash('このページにアクセスするにはログインが必要です', 'warning')
        return redirect(url_for('index'))
    
    return render_template('protected.html', user=user, provider_name=PROVIDER_NAME)

# === クラス・インスタンス管理機能 ===

def require_login(f):
    """ログイン必須デコレータ"""
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user:
            flash('このページにアクセスするにはログインが必要です', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_view_date():
    """リクエストからview_dateパラメータを取得し、有効な日付を返す"""
    view_date_str = request.args.get('view_date')
    
    if not view_date_str:
        # パラメータがない場合は現在日を返す
        return date.today()
    
    try:
        # YYYY-MM-DD 形式の文字列を日付オブジェクトに変換
        return datetime.strptime(view_date_str, '%Y-%m-%d').date()
    except ValueError:
        # 無効な日付形式の場合は現在日を返す
        return date.today()

@app.route('/classes')
@require_login
def classes_index():
    """クラス管理トップページ"""
    user = session.get('user')
    view_date = get_view_date()
    
    try:
        entity_metas = EntityMetaRepository.get_all()
        return render_template('classes/index.html', 
                             entity_metas=entity_metas,
                             view_date=view_date,
                             user=user, 
                             provider_name=PROVIDER_NAME)
    except Exception as e:
        flash(f'データの取得に失敗しました: {str(e)}', 'error')
        return render_template('classes/index.html', 
                             entity_metas=[],
                             view_date=view_date,
                             user=user, 
                             provider_name=PROVIDER_NAME)

@app.route('/classes/create', methods=['POST'])
@require_login
def create_entity_meta():
    """エンティティメタ作成"""
    try:
        title = request.form.get('title', '').strip()
        
        # バリデーション
        if not title:
            flash('エンティティタイプ名を入力してください。', 'error')
            return redirect(url_for('classes_index'))
        
        if len(title) > 100:
            flash('エンティティタイプ名は100文字以内で入力してください。', 'error')
            return redirect(url_for('classes_index'))
        
        # 重複チェック
        if EntityMetaRepository.exists_by_title(title):
            flash(f'「{title}」は既に登録されています。', 'error')
            return redirect(url_for('classes_index'))
        
        # エンティティメタを作成
        entity_meta_id = EntityMetaRepository.create(title)
        
        flash(f'エンティティタイプ「{title}」を登録しました。', 'success')
        return redirect(url_for('classes_index'))
        
    except Exception as e:
        print(f'Error creating entity meta: {e}')
        flash('エンティティメタの登録中にエラーが発生しました。', 'error')
        return redirect(url_for('classes_index'))

@app.route('/classes/<int:entity_meta_id>/attributes')
@require_login
def manage_attributes(entity_meta_id):
    """属性管理ページ"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('classes_index'))
        
        # 属性メタ一覧を取得
        attributes = AttributeMetaRepository.get_by_entity_meta_id(entity_meta_id)
        
        return render_template('classes/manage_attributes.html',
                             entity_meta=entity_meta,
                             attributes=attributes,
                             user=session.get('user'),
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        print(f'Error in manage_attributes: {e}')
        flash('データの取得に失敗しました。', 'error')
        return redirect(url_for('classes_index'))

@app.route('/classes/<int:entity_meta_id>/attributes/create', methods=['POST'])
@require_login
def create_attribute(entity_meta_id):
    """属性作成"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('classes_index'))
        
        title = request.form.get('title', '').strip()
        data_type = request.form.get('data_type', '').strip()
        order_display = request.form.get('order_display', '').strip()
        
        # バリデーション
        if not title:
            flash('属性名を入力してください。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        if len(title) > 100:
            flash('属性名は100文字以内で入力してください。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        if not data_type:
            flash('データ型を選択してください。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # 重複チェック
        if AttributeMetaRepository.exists_by_title_and_entity(title, entity_meta_id):
            flash(f'「{title}」は既に登録されています。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # order_displayの処理
        order_display_value = None
        if order_display:
            try:
                order_display_value = int(order_display)
                if order_display_value < 1 or order_display_value > 999:
                    flash('表示順は1から999の範囲で入力してください。', 'error')
                    return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
            except ValueError:
                flash('表示順は数値で入力してください。', 'error')
                return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # 属性メタを作成
        attribute_meta_id = AttributeMetaRepository.create(title, entity_meta_id, data_type, order_display_value)
        
        flash(f'属性「{title}」を追加しました。', 'success')
        return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
    except Exception as e:
        print(f'Error creating attribute: {e}')
        flash('属性の追加中にエラーが発生しました。', 'error')
        return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))

@app.route('/classes/<int:entity_meta_id>/attributes/update', methods=['POST'])
@require_login
def update_attribute(entity_meta_id):
    """属性更新"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('classes_index'))
        
        attribute_id = request.form.get('attribute_id')
        title = request.form.get('title', '').strip()
        data_type = request.form.get('data_type', '').strip()
        order_display = request.form.get('order_display', '').strip()
        
        if not attribute_id:
            flash('属性IDが指定されていません。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        try:
            attribute_id = int(attribute_id)
        except ValueError:
            flash('無効な属性IDです。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # 属性の存在確認
        existing_attribute = AttributeMetaRepository.get_by_id(attribute_id)
        if not existing_attribute or existing_attribute['entity_id'] != entity_meta_id:
            flash('指定された属性が見つかりません。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # バリデーション
        if not title:
            flash('属性名を入力してください。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        if len(title) > 100:
            flash('属性名は100文字以内で入力してください。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        if not data_type:
            flash('データ型を選択してください。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # 重複チェック（自分以外）
        if AttributeMetaRepository.exists_by_title_and_entity(title, entity_meta_id, attribute_id):
            flash(f'「{title}」は既に登録されています。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # order_displayの処理
        order_display_value = None
        if order_display:
            try:
                order_display_value = int(order_display)
                if order_display_value < 1 or order_display_value > 999:
                    flash('表示順は1から999の範囲で入力してください。', 'error')
                    return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
            except ValueError:
                flash('表示順は数値で入力してください。', 'error')
                return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # 属性メタを更新
        success = AttributeMetaRepository.update(attribute_id, title, data_type, order_display_value)
        
        if success:
            flash(f'属性「{title}」を更新しました。', 'success')
        else:
            flash('属性の更新に失敗しました。', 'error')
        
        return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
    except Exception as e:
        print(f'Error updating attribute: {e}')
        flash('属性の更新中にエラーが発生しました。', 'error')
        return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))

@app.route('/classes/<int:entity_meta_id>/attributes/delete', methods=['POST'])
@require_login
def delete_attribute(entity_meta_id):
    """属性削除"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('classes_index'))
        
        attribute_id = request.form.get('attribute_id')
        
        if not attribute_id:
            flash('属性IDが指定されていません。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        try:
            attribute_id = int(attribute_id)
        except ValueError:
            flash('無効な属性IDです。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # 属性の存在確認
        existing_attribute = AttributeMetaRepository.get_by_id(attribute_id)
        if not existing_attribute or existing_attribute['entity_id'] != entity_meta_id:
            flash('指定された属性が見つかりません。', 'error')
            return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
        # 属性メタを削除
        success = AttributeMetaRepository.delete(attribute_id)
        
        if success:
            flash(f'属性「{existing_attribute["title"]}」を削除しました。', 'success')
        else:
            flash('属性の削除に失敗しました。', 'error')
        
        return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))
        
    except Exception as e:
        print(f'Error deleting attribute: {e}')
        flash('属性の削除中にエラーが発生しました。', 'error')
        return redirect(url_for('manage_attributes', entity_meta_id=entity_meta_id))

@app.route('/instances')
@require_login
def instances_list():
    """インスタンス一覧ページ"""
    user = session.get('user')
    entity_type = request.args.get('type')
    view_date = get_view_date()
    
    # 日付を文字列形式に変換（SQLite用）
    view_date_str = view_date.strftime('%Y-%m-%d')
    
    try:
        if entity_type:
            # entity_typeを整数に変換
            try:
                entity_type_id = int(entity_type)
                entities = EntityRepository.get_by_type_at_date(entity_type_id, view_date_str)
            except (ValueError, TypeError):
                flash('無効なエンティティタイプです', 'error')
                return redirect(url_for('instances_list'))
        else:
            entities = EntityRepository.get_all_at_date(view_date_str)
        
        entity_types = EntityMetaRepository.get_all()
        
        return render_template('instances/list.html', 
                             entities=entities, 
                             entity_types=entity_types,
                             current_type=entity_type,
                             view_date=view_date,
                             user=user, 
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        flash(f'データの取得に失敗しました: {str(e)}', 'error')
        return render_template('instances/list.html', 
                             entities=[], 
                             entity_types=[],
                             current_type=entity_type,
                             view_date=view_date,
                             user=user, 
                             provider_name=PROVIDER_NAME)

@app.route('/instances/<int:entity_id>')
@require_login
def instance_detail(entity_id):
    """インスタンス詳細ページ"""
    user = session.get('user')
    view_date = get_view_date()
    
    # 日付を文字列形式に変換（SQLite用）
    view_date_str = view_date.strftime('%Y-%m-%d')
    
    try:
        # エンティティ基本情報
        entity = EntityRepository.get_by_id(entity_id)
        
        if not entity:
            flash('エンティティが見つかりません', 'error')
            return redirect(url_for('instances_list'))
        
        # 属性情報（指定日付時点での最新値）
        attributes = AttributeRepository.get_by_entity_id_at_date(entity_id, view_date_str)
        
        # 属性を通常の属性とリレーションに分類
        regular_attributes = []
        relation_attributes = []
        
        for attr in attributes:
            if attr['data_type'] == 'ENTITY':
                relation_attributes.append(attr)
            else:
                regular_attributes.append(attr)
        
        return render_template('instances/detail.html', 
                             entity=entity,
                             attributes=regular_attributes,
                             relations=relation_attributes,
                             view_date=view_date,
                             user=user, 
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        flash(f'データの取得に失敗しました: {str(e)}', 'error')
        return redirect(url_for('instances_list'))

@app.route('/instances/create', methods=['GET'])
@require_login
def create_instance_form():
    """インスタンス作成フォーム"""
    entity_type = request.args.get('type')
    
    try:
        # エンティティタイプが指定されている場合は、そのタイプの属性メタを取得
        if entity_type:
            try:
                entity_type_id = int(entity_type)
                entity_meta = EntityMetaRepository.get_by_id(entity_type_id)
                if not entity_meta:
                    flash('指定されたエンティティタイプが見つかりません', 'error')
                    return redirect(url_for('instances_list'))
                
                attribute_metas = AttributeMetaRepository.get_by_entity_meta_id(entity_type_id)
            except (ValueError, TypeError):
                flash('無効なエンティティタイプです', 'error')
                return redirect(url_for('instances_list'))
        else:
            entity_meta = None
            attribute_metas = []
        
        # 全エンティティタイプを取得（セレクトボックス用）
        entity_types = EntityMetaRepository.get_all()
        
        return render_template('instances/create.html',
                             entity_meta=entity_meta,
                             attribute_metas=attribute_metas,
                             entity_types=entity_types,
                             selected_type=entity_type,
                             user=session.get('user'),
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        print(f'Error in create_entity_form: {e}')
        flash('フォームの表示中にエラーが発生しました。', 'error')
        return redirect(url_for('instances_list'))

@app.route('/instances/create', methods=['POST'])
@require_login
def create_instance():
    """インスタンス作成実行"""
    try:
        title = request.form.get('title', '').strip()
        class_id = request.form.get('class_id', '').strip()
        date_in = request.form.get('date_in', '').strip() or None
        date_out = request.form.get('date_out', '').strip() or None
        
        # バリデーション
        if not title:
            flash('エンティティ名を入力してください。', 'error')
            return redirect(request.url)
        
        if len(title) > 200:
            flash('エンティティ名は200文字以内で入力してください。', 'error')
            return redirect(request.url)
        
        if not class_id:
            flash('エンティティタイプを選択してください。', 'error')
            return redirect(request.url)
        
        try:
            class_id = int(class_id)
        except ValueError:
            flash('無効なエンティティタイプです。', 'error')
            return redirect(request.url)
        
        # エンティティクラスの存在確認
        entity_class = EntityMetaRepository.get_by_id(class_id)
        if not entity_class:
            flash('指定されたエンティティタイプが存在しません。', 'error')
            return redirect(request.url)
        
        # エンティティを作成
        entity_id = EntityRepository.create(title, class_id, date_in, date_out)
        
        # 属性値の保存
        attribute_classes = AttributeMetaRepository.get_by_entity_meta_id(class_id)
        for attr_class in attribute_classes:
            attr_value = request.form.get(f'attr_{attr_class["identifier"]}', '').strip()
            if attr_value:  # 空でない場合のみ保存
                if attr_class['data_type'] == 'ENTITY':
                    # ENTITY型の場合はエンティティIDを文字列として保存
                    try:
                        target_entity_id = int(attr_value)  # バリデーション用
                        AttributeRepository.create(str(target_entity_id), attr_class['identifier'], entity_id)
                    except ValueError:
                        flash(f'属性「{attr_class["title"]}」の値が無効です。', 'warning')
                else:
                    # 通常の属性の場合
                    AttributeRepository.create(attr_value, attr_class['identifier'], entity_id)
        
        flash(f'エンティティ「{title}」を作成しました。', 'success')
        return redirect(url_for('instance_detail', entity_id=entity_id))
        
    except Exception as e:
        print(f'Error creating entity: {e}')
        flash('エンティティの作成中にエラーが発生しました。', 'error')
        return redirect(url_for('instances_list'))

@app.route('/instances/<int:entity_id>/edit', methods=['GET'])
@require_login
def edit_instance(entity_id):
    """インスタンス編集フォーム"""
    user = session.get('user')
    view_date = get_view_date()
    
    # 日付を文字列形式に変換（SQLite用）
    view_date_str = view_date.strftime('%Y-%m-%d')
    
    try:
        # エンティティ基本情報
        entity = EntityRepository.get_by_id(entity_id)
        
        if not entity:
            flash('エンティティが見つかりません', 'error')
            return redirect(url_for('instances_list'))
        
        # 属性情報（指定日付時点での最新値）
        attributes = AttributeRepository.get_by_entity_id_at_date(entity_id, view_date_str)
        
        # 属性を通常の属性とリレーションに分類
        regular_attributes = []
        relation_attributes = []
        
        for attr in attributes:
            if attr['data_type'] == 'ENTITY':
                relation_attributes.append(attr)
            else:
                regular_attributes.append(attr)
        
        return render_template('instances/edit.html', 
                             entity=entity,
                             attributes=regular_attributes,
                             relations=relation_attributes,
                             view_date=view_date,
                             user=user, 
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        print(f'Error in edit_entity: {e}')
        flash('エンティティ編集フォームの表示中にエラーが発生しました。', 'error')
        return redirect(url_for('instance_detail', entity_id=entity_id))

@app.route('/instances/<int:entity_id>/edit', methods=['POST'])
@require_login
def update_instance(entity_id):
    """インスタンス更新実行"""
    try:
        # エンティティの存在確認
        entity = EntityRepository.get_by_id(entity_id)
        if not entity:
            flash('エンティティが見つかりません', 'error')
            return redirect(url_for('instances_list'))
        
        title = request.form.get('title', '').strip()
        date_in = request.form.get('date_in', '').strip() or None
        date_out = request.form.get('date_out', '').strip() or None
        
        # バリデーション
        if not title:
            flash('エンティティ名を入力してください。', 'error')
            return redirect(url_for('edit_instance', entity_id=entity_id))
        
        if len(title) > 200:
            flash('エンティティ名は200文字以内で入力してください。', 'error')
            return redirect(url_for('edit_instance', entity_id=entity_id))
        
        # エンティティを更新
        success = EntityRepository.update(entity_id, title=title, date_in=date_in, date_out=date_out)
        
        if success:
            flash(f'エンティティ「{title}」を更新しました。', 'success')
            return redirect(url_for('instance_detail', entity_id=entity_id))
        else:
            flash('エンティティの更新に失敗しました。', 'error')
            return redirect(url_for('edit_instance', entity_id=entity_id))
        
    except Exception as e:
        print(f'Error updating entity: {e}')
        flash('エンティティの更新中にエラーが発生しました。', 'error')
        return redirect(url_for('edit_instance', entity_id=entity_id))

@app.route('/instances/<int:entity_id>/attribute/update', methods=['POST'])
@require_login
def update_attribute_value(entity_id):
    """属性値更新"""
    try:
        # エンティティの存在確認
        entity = EntityRepository.get_by_id(entity_id)
        if not entity:
            flash('エンティティが見つかりません', 'error')
            return redirect(url_for('instances_list'))
        
        attribute_id = request.form.get('attribute_id')
        attribute_value = request.form.get('attribute_value', '').strip()
        
        if not attribute_id:
            flash('属性IDが指定されていません。', 'error')
            return redirect(url_for('edit_instance', entity_id=entity_id))
        
        try:
            attribute_id = int(attribute_id)
        except ValueError:
            flash('無効な属性IDです。', 'error')
            return redirect(url_for('edit_instance', entity_id=entity_id))
        
        # 属性値を更新
        success = AttributeRepository.update(attribute_id, title=attribute_value)
        
        if success:
            flash('属性値を更新しました。', 'success')
        else:
            flash('属性値の更新に失敗しました。', 'error')
        
        return redirect(url_for('edit_instance', entity_id=entity_id))
        
    except Exception as e:
        print(f'Error updating attribute value: {e}')
        flash('属性値の更新中にエラーが発生しました。', 'error')
        return redirect(url_for('edit_instance', entity_id=entity_id))

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
