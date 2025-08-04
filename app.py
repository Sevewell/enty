from flask import Flask, render_template, redirect, url_for, session, flash, request
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
from db import (
    EntityMetaRepository, 
    EntityRepository, 
    AttributeRepository, 
    RelationRepository,
    AttributeMetaRepository,
    RelationMetaRepository
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
    return render_template('index.html', user=user, provider_name=PROVIDER_NAME)

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

# === 資産管理機能 ===

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

@app.route('/assets')
@require_login
def assets_index():
    """資産管理トップページ"""
    user = session.get('user')
    
    try:
        entity_metas = EntityMetaRepository.get_all()
        return render_template('assets/index.html', 
                             entity_metas=entity_metas,
                             user=user, 
                             provider_name=PROVIDER_NAME)
    except Exception as e:
        flash(f'データの取得に失敗しました: {str(e)}', 'error')
        return render_template('assets/index.html', 
                             entity_metas=[],
                             user=user, 
                             provider_name=PROVIDER_NAME)

@app.route('/assets/entity-meta/create', methods=['POST'])
@require_login
def create_entity_meta():
    """エンティティメタ作成"""
    try:
        title = request.form.get('title', '').strip()
        
        # バリデーション
        if not title:
            flash('エンティティタイプ名を入力してください。', 'error')
            return redirect(url_for('assets_index'))
        
        if len(title) > 100:
            flash('エンティティタイプ名は100文字以内で入力してください。', 'error')
            return redirect(url_for('assets_index'))
        
        # 重複チェック
        if EntityMetaRepository.exists_by_title(title):
            flash(f'「{title}」は既に登録されています。', 'error')
            return redirect(url_for('assets_index'))
        
        # エンティティメタを作成
        entity_meta_id = EntityMetaRepository.create(title)
        
        flash(f'エンティティタイプ「{title}」を登録しました。', 'success')
        return redirect(url_for('assets_index'))
        
    except Exception as e:
        print(f'Error creating entity meta: {e}')
        flash('エンティティメタの登録中にエラーが発生しました。', 'error')
        return redirect(url_for('assets_index'))

@app.route('/assets/entity-meta/<int:entity_meta_id>/attributes')
@require_login
def manage_attributes(entity_meta_id):
    """属性管理ページ"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('assets_index'))
        
        # 属性メタ一覧を取得
        attributes = AttributeMetaRepository.get_by_entity_meta_id(entity_meta_id)
        
        return render_template('assets/manage_attributes.html',
                             entity_meta=entity_meta,
                             attributes=attributes,
                             user=session.get('user'),
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        print(f'Error in manage_attributes: {e}')
        flash('データの取得に失敗しました。', 'error')
        return redirect(url_for('assets_index'))

@app.route('/assets/entity-meta/<int:entity_meta_id>/attributes/create', methods=['POST'])
@require_login
def create_attribute(entity_meta_id):
    """属性作成"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('assets_index'))
        
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

@app.route('/assets/entity-meta/<int:entity_meta_id>/attributes/update', methods=['POST'])
@require_login
def update_attribute(entity_meta_id):
    """属性更新"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('assets_index'))
        
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

@app.route('/assets/entity-meta/<int:entity_meta_id>/attributes/delete', methods=['POST'])
@require_login
def delete_attribute(entity_meta_id):
    """属性削除"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('assets_index'))
        
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

@app.route('/assets/entity-meta/<int:entity_meta_id>/relations')
@require_login
def manage_relations(entity_meta_id):
    """リレーション管理ページ"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('assets_index'))
        
        # リレーションメタ一覧を取得
        relations = RelationMetaRepository.get_by_entity_meta_id(entity_meta_id)
        
        # 全エンティティタイプを取得（セレクトボックス用）
        entity_types = EntityMetaRepository.get_all()
        
        return render_template('assets/manage_relations.html',
                             entity_meta=entity_meta,
                             relations=relations,
                             entity_types=entity_types,
                             user=session.get('user'),
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        print(f'Error in manage_relations: {e}')
        flash('データの取得に失敗しました。', 'error')
        return redirect(url_for('assets_index'))

@app.route('/assets/entity-meta/<int:entity_meta_id>/relations/create', methods=['POST'])
@require_login
def create_relation(entity_meta_id):
    """リレーション作成"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('assets_index'))
        
        title = request.form.get('title', '').strip()
        from_entity_id = request.form.get('from_entity_id', '').strip()
        to_entity_id = request.form.get('to_entity_id', '').strip()
        
        # バリデーション
        if not title:
            flash('リレーション名を入力してください。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        if len(title) > 100:
            flash('リレーション名は100文字以内で入力してください。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        if not from_entity_id:
            flash('開始エンティティを選択してください。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        if not to_entity_id:
            flash('終了エンティティを選択してください。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        try:
            from_entity_id = int(from_entity_id)
            to_entity_id = int(to_entity_id)
        except ValueError:
            flash('無効なエンティティIDです。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        if from_entity_id == to_entity_id:
            flash('開始エンティティと終了エンティティは異なるものを選択してください。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # エンティティクラスの存在確認
        if not EntityMetaRepository.get_by_id(from_entity_id) or not EntityMetaRepository.get_by_id(to_entity_id):
            flash('指定されたエンティティタイプが存在しません。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # 重複チェック
        if RelationMetaRepository.exists_by_title_and_entities(title, from_entity_id, to_entity_id):
            flash(f'同じ組み合わせで「{title}」は既に登録されています。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # リレーションクラスを作成
        relation_class_id = RelationMetaRepository.create(title, from_entity_id, to_entity_id)
        
        flash(f'リレーション「{title}」を追加しました。', 'success')
        return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
    except Exception as e:
        print(f'Error creating relation: {e}')
        flash('リレーションの追加中にエラーが発生しました。', 'error')
        return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))

@app.route('/assets/entity-meta/<int:entity_meta_id>/relations/update', methods=['POST'])
@require_login
def update_relation(entity_meta_id):
    """リレーション更新"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('assets_index'))
        
        relation_id = request.form.get('relation_id')
        title = request.form.get('title', '').strip()
        from_entity_id = request.form.get('from_entity_id', '').strip()
        to_entity_id = request.form.get('to_entity_id', '').strip()
        
        if not relation_id:
            flash('リレーションIDが指定されていません。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        try:
            relation_id = int(relation_id)
            from_entity_id = int(from_entity_id)
            to_entity_id = int(to_entity_id)
        except ValueError:
            flash('無効なIDです。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # リレーションの存在確認
        existing_relation = RelationMetaRepository.get_by_id(relation_id)
        if not existing_relation:
            flash('指定されたリレーションが見つかりません。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # バリデーション
        if not title:
            flash('リレーション名を入力してください。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        if len(title) > 100:
            flash('リレーション名は100文字以内で入力してください。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        if from_entity_id == to_entity_id:
            flash('開始エンティティと終了エンティティは異なるものを選択してください。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # エンティティクラスの存在確認
        if not EntityMetaRepository.get_by_id(from_entity_id) or not EntityMetaRepository.get_by_id(to_entity_id):
            flash('指定されたエンティティタイプが存在しません。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # 重複チェック（自分以外）
        if RelationMetaRepository.exists_by_title_and_entities(title, from_entity_id, to_entity_id, relation_id):
            flash(f'同じ組み合わせで「{title}」は既に登録されています。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # リレーションクラスを更新
        success = RelationMetaRepository.update(relation_id, title, from_entity_id, to_entity_id)
        
        if success:
            flash(f'リレーション「{title}」を更新しました。', 'success')
        else:
            flash('リレーションの更新に失敗しました。', 'error')
        
        return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
    except Exception as e:
        print(f'Error updating relation: {e}')
        flash('リレーションの更新中にエラーが発生しました。', 'error')
        return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))

@app.route('/assets/entity-meta/<int:entity_meta_id>/relations/delete', methods=['POST'])
@require_login
def delete_relation(entity_meta_id):
    """リレーション削除"""
    try:
        # エンティティメタの存在確認
        entity_meta = EntityMetaRepository.get_by_id(entity_meta_id)
        if not entity_meta:
            flash('指定されたエンティティタイプが見つかりません。', 'error')
            return redirect(url_for('assets_index'))
        
        relation_id = request.form.get('relation_id')
        
        if not relation_id:
            flash('リレーションIDが指定されていません。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        try:
            relation_id = int(relation_id)
        except ValueError:
            flash('無効なリレーションIDです。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # リレーションの存在確認
        existing_relation = RelationMetaRepository.get_by_id(relation_id)
        if not existing_relation:
            flash('指定されたリレーションが見つかりません。', 'error')
            return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
        # リレーションメタを削除
        success = RelationMetaRepository.delete(relation_id)
        
        if success:
            flash(f'リレーション「{existing_relation["title"]}」を削除しました。', 'success')
        else:
            flash('リレーションの削除に失敗しました。', 'error')
        
        return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))
        
    except Exception as e:
        print(f'Error deleting relation: {e}')
        flash('リレーションの削除中にエラーが発生しました。', 'error')
        return redirect(url_for('manage_relations', entity_meta_id=entity_meta_id))

@app.route('/assets/entities')
@require_login
def entity_list():
    """エンティティ一覧ページ"""
    user = session.get('user')
    entity_type = request.args.get('type')
    
    try:
        if entity_type:
            # entity_typeを整数に変換
            try:
                entity_type_id = int(entity_type)
                entities = EntityRepository.get_by_type(entity_type_id)
            except (ValueError, TypeError):
                flash('無効なエンティティタイプです', 'error')
                return redirect(url_for('entity_list'))
        else:
            entities = EntityRepository.get_all()
        
        entity_types = EntityMetaRepository.get_all()
        
        return render_template('assets/entities.html', 
                             entities=entities, 
                             entity_types=entity_types,
                             current_type=entity_type,
                             user=user, 
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        flash(f'データの取得に失敗しました: {str(e)}', 'error')
        return render_template('assets/entities.html', 
                             entities=[], 
                             entity_types=[],
                             current_type=entity_type,
                             user=user, 
                             provider_name=PROVIDER_NAME)

@app.route('/assets/entity/<int:entity_id>')
@require_login
def entity_detail(entity_id):
    """エンティティ詳細ページ"""
    user = session.get('user')
    
    try:
        # エンティティ基本情報
        entity = EntityRepository.get_by_id(entity_id)
        
        if not entity:
            flash('エンティティが見つかりません', 'error')
            return redirect(url_for('entity_list'))
        
        # 属性情報
        attributes = AttributeRepository.get_by_entity_id(entity_id)
        
        # リレーション情報
        relations_from = RelationRepository.get_relations_from(entity_id)
        relations_to = RelationRepository.get_relations_to(entity_id)
        
        return render_template('assets/entity_detail.html', 
                             entity=entity,
                             attributes=attributes,
                             relations_from=relations_from,
                             relations_to=relations_to,
                             user=user, 
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        flash(f'データの取得に失敗しました: {str(e)}', 'error')
        return redirect(url_for('entity_list'))

@app.route('/assets/entity/create', methods=['GET'])
@require_login
def create_entity_form():
    """エンティティ作成フォーム"""
    entity_type = request.args.get('type')
    
    try:
        # エンティティタイプが指定されている場合は、そのタイプの属性メタを取得
        if entity_type:
            try:
                entity_type_id = int(entity_type)
                entity_meta = EntityMetaRepository.get_by_id(entity_type_id)
                if not entity_meta:
                    flash('指定されたエンティティタイプが見つかりません', 'error')
                    return redirect(url_for('entity_list'))
                
                attribute_metas = AttributeMetaRepository.get_by_entity_meta_id(entity_type_id)
            except (ValueError, TypeError):
                flash('無効なエンティティタイプです', 'error')
                return redirect(url_for('entity_list'))
        else:
            entity_meta = None
            attribute_metas = []
        
        # 全エンティティタイプを取得（セレクトボックス用）
        entity_types = EntityMetaRepository.get_all()
        
        return render_template('assets/create_entity.html',
                             entity_meta=entity_meta,
                             attribute_metas=attribute_metas,
                             entity_types=entity_types,
                             selected_type=entity_type,
                             user=session.get('user'),
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        print(f'Error in create_entity_form: {e}')
        flash('フォームの表示中にエラーが発生しました。', 'error')
        return redirect(url_for('entity_list'))

@app.route('/assets/entity/create', methods=['POST'])
@require_login
def create_entity():
    """エンティティ作成実行"""
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
                AttributeRepository.create(attr_value, attr_class['identifier'], entity_id)
        
        flash(f'エンティティ「{title}」を作成しました。', 'success')
        return redirect(url_for('entity_detail', entity_id=entity_id))
        
    except Exception as e:
        print(f'Error creating entity: {e}')
        flash('エンティティの作成中にエラーが発生しました。', 'error')
        return redirect(url_for('entity_list'))

@app.route('/assets/entity/<int:entity_id>/edit', methods=['GET'])
@require_login
def edit_entity(entity_id):
    """エンティティ編集フォーム"""
    user = session.get('user')
    
    try:
        # エンティティ基本情報
        entity = EntityRepository.get_by_id(entity_id)
        
        if not entity:
            flash('エンティティが見つかりません', 'error')
            return redirect(url_for('entity_list'))
        
        # 属性情報
        attributes = AttributeRepository.get_by_entity_id(entity_id)
        
        return render_template('assets/edit_entity.html', 
                             entity=entity,
                             attributes=attributes,
                             user=user, 
                             provider_name=PROVIDER_NAME)
    
    except Exception as e:
        print(f'Error in edit_entity: {e}')
        flash('エンティティ編集フォームの表示中にエラーが発生しました。', 'error')
        return redirect(url_for('entity_detail', entity_id=entity_id))

@app.route('/assets/entity/<int:entity_id>/edit', methods=['POST'])
@require_login
def update_entity(entity_id):
    """エンティティ更新実行"""
    try:
        # エンティティの存在確認
        entity = EntityRepository.get_by_id(entity_id)
        if not entity:
            flash('エンティティが見つかりません', 'error')
            return redirect(url_for('entity_list'))
        
        title = request.form.get('title', '').strip()
        date_in = request.form.get('date_in', '').strip() or None
        date_out = request.form.get('date_out', '').strip() or None
        
        # バリデーション
        if not title:
            flash('エンティティ名を入力してください。', 'error')
            return redirect(url_for('edit_entity', entity_id=entity_id))
        
        if len(title) > 200:
            flash('エンティティ名は200文字以内で入力してください。', 'error')
            return redirect(url_for('edit_entity', entity_id=entity_id))
        
        # エンティティを更新
        success = EntityRepository.update(entity_id, title=title, date_in=date_in, date_out=date_out)
        
        if success:
            flash(f'エンティティ「{title}」を更新しました。', 'success')
            return redirect(url_for('entity_detail', entity_id=entity_id))
        else:
            flash('エンティティの更新に失敗しました。', 'error')
            return redirect(url_for('edit_entity', entity_id=entity_id))
        
    except Exception as e:
        print(f'Error updating entity: {e}')
        flash('エンティティの更新中にエラーが発生しました。', 'error')
        return redirect(url_for('edit_entity', entity_id=entity_id))

@app.route('/assets/entity/<int:entity_id>/attribute/update', methods=['POST'])
@require_login
def update_attribute_value(entity_id):
    """属性値更新"""
    try:
        # エンティティの存在確認
        entity = EntityRepository.get_by_id(entity_id)
        if not entity:
            flash('エンティティが見つかりません', 'error')
            return redirect(url_for('entity_list'))
        
        attribute_id = request.form.get('attribute_id')
        attribute_value = request.form.get('attribute_value', '').strip()
        
        if not attribute_id:
            flash('属性IDが指定されていません。', 'error')
            return redirect(url_for('edit_entity', entity_id=entity_id))
        
        try:
            attribute_id = int(attribute_id)
        except ValueError:
            flash('無効な属性IDです。', 'error')
            return redirect(url_for('edit_entity', entity_id=entity_id))
        
        # 属性値を更新
        success = AttributeRepository.update(attribute_id, title=attribute_value)
        
        if success:
            flash('属性値を更新しました。', 'success')
        else:
            flash('属性値の更新に失敗しました。', 'error')
        
        return redirect(url_for('edit_entity', entity_id=entity_id))
        
    except Exception as e:
        print(f'Error updating attribute value: {e}')
        flash('属性値の更新中にエラーが発生しました。', 'error')
        return redirect(url_for('edit_entity', entity_id=entity_id))

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
