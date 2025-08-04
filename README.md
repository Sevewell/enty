# Flask OIDC Authentication & Asset Management Application

AuthlibとFlaskを使用したOpenID Connect認証と資産管理機能を統合したWebアプリケーションです。任意のOIDCプロバイダー（Keycloak、Azure AD、Auth0、Google、GitHub等）と連携可能で、組織の人員やデバイス等の資産管理が行えます。

## 機能

### 認証機能
- OpenID Connect（OIDC）認証
- 汎用OIDCプロバイダー対応
- ユーザープロフィール表示
- 保護されたページ（認証が必要）
- セッション管理
- ログイン・ログアウト機能

### 資産管理機能
- **エンティティ管理**: 人員、デバイス、ソフトウェア、オフィス機器の管理
- **属性管理**: 各エンティティの詳細属性（メタデータドリブン）
- **リレーション管理**: エンティティ間の関係性（使用中、インストール済み等）
- **ダッシュボード**: 資産の統計情報と最近の活動
- **検索・フィルタ**: エンティティの検索とタイプ別フィルタリング
- **詳細表示**: エンティティの詳細情報とリレーション表示
- **時系列管理**: 登録日、無効化日、イベント日の管理

## 依存関係

このアプリケーションは外部ツールへの依存を最小限に抑えた設計です。

### Pythonライブラリ
- **Flask**: Webフレームワーク
- **Authlib**: OIDC認証ライブラリ
- **python-dotenv**: 環境変数管理
- **SQLite3**: データベース（Python標準ライブラリ）

### フロントエンド
- **自作CSS**: Bootstrap等の外部CSSフレームワークに依存しない独自スタイル
- **Vanilla JavaScript**: ライブラリ不要のシンプルなスクリプト
- **PC向けデザイン**: 1200px固定幅のデスクトップブラウザ向けUI
- **シンプル設計**: レスポンシブ不要の安定したレイアウト

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. OIDCプロバイダーの設定

#### 例：Keycloak
1. Keycloakの管理コンソールにアクセス
2. 新しいクライアントを作成
3. Client IDとClient Secretを取得
4. Valid Redirect URIsに以下を追加：
   - `http://localhost:5000/authorize`

#### 例：Azure AD
1. Azure Portalにアクセス
2. Azure Active Directoryで新しいアプリケーションを登録
3. Application IDとClient Secretを取得
4. Redirect URIsに以下を追加：
   - `http://localhost:5000/authorize`

#### 例：Auth0
1. Auth0ダッシュボードにアクセス
2. 新しいアプリケーションを作成
3. Client IDとClient Secretを取得
4. Allowed Callback URLsに以下を追加：
   - `http://localhost:5000/authorize`

### 3. 環境変数の設定

`.env.example`を`.env`にコピーして、適切な値を設定：

```bash
cp .env.example .env
```

`.env`ファイルを編集して、OIDC設定を追加：

```env
SECRET_KEY=your-secret-key-here
OIDC_METADATA_URL=https://your-oidc-provider/.well-known/openid-configuration
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_SCOPE=openid profile email
OIDC_PROVIDER_NAME=Your Provider Name
```

### 4. アプリケーションの起動

```bash
python app.py
```

初回起動時に自動的にSQLiteデータベース（`assets.db`）が作成され、サンプルデータが投入されます。

ブラウザで `http://localhost:5000` にアクセス

## 設定例

### Keycloak
```env
OIDC_METADATA_URL=https://keycloak.example.com/auth/realms/myrealm/.well-known/openid-configuration
OIDC_CLIENT_ID=flask-app
OIDC_CLIENT_SECRET=your-client-secret
OIDC_PROVIDER_NAME=Keycloak
```

### Azure AD
```env
OIDC_METADATA_URL=https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration
OIDC_CLIENT_ID=your-application-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_PROVIDER_NAME=Azure AD
```

### Auth0
```env
OIDC_METADATA_URL=https://your-domain.auth0.com/.well-known/openid-configuration
OIDC_CLIENT_ID=your-client-id
OIDC_CLIENT_SECRET=your-client-secret
OIDC_PROVIDER_NAME=Auth0
```

### Google
```env
OIDC_METADATA_URL=https://accounts.google.com/.well-known/openid-configuration
OIDC_CLIENT_ID=your-google-client-id
OIDC_CLIENT_SECRET=your-google-client-secret
OIDC_PROVIDER_NAME=Google
```

## ファイル構成

```
/projects/enty/
├── app.py                 # メインアプリケーション（認証、資産管理機能）
├── init.sql               # データベーススキーマ定義
├── init_db.py            # データベース初期化スクリプト
├── assets.db             # SQLiteデータベース（自動生成）
├── requirements.txt       # 依存関係
├── .env.example          # 環境変数の例
├── README.md             # このファイル
├── static/               # 静的ファイル
│   └── style.css         # カスタムCSS
└── templates/            # HTMLテンプレート
    ├── base.html         # ベーステンプレート
    ├── index.html        # ホームページ
    ├── profile.html      # プロフィールページ
    ├── protected.html    # 保護されたページ
    └── assets/           # 資産管理用テンプレート
        ├── dashboard.html    # 資産管理ダッシュボード
        ├── entities.html     # エンティティ一覧
        └── entity_detail.html # エンティティ詳細
```

## 使用方法

### 認証機能
1. ホームページでログインボタンをクリック
2. 設定したOIDCプロバイダーでログイン
3. プロフィールページでユーザー情報を確認
4. ログアウトボタンでセッションを終了

### 資産管理機能
1. **ダッシュボードにアクセス** (`/assets`)
   - 各エンティティタイプの統計情報を表示
   - 最近追加されたエンティティを確認
   - クイックアクションリンクで各種一覧にアクセス

2. **エンティティ一覧を閲覧** (`/assets/entities`)
   - 全エンティティまたはタイプ別でフィルタリング
   - 検索機能で特定のエンティティを検索
   - エンティティの状態（有効/無効）を確認

3. **エンティティ詳細を表示** (`/assets/entity/<id>`)
   - エンティティの基本情報（ID、名前、タイプ、登録日等）
   - 属性情報（メールアドレス、部署、シリアル番号等）
   - リレーション情報（使用中のデバイス、インストール済みソフト等）

## データベース設計

### エンティティリレーションモデル (ERM)

アプリケーションはメタデータドリブンなERMを使用しています。これにより、柔軟なデータ構造を実現しています。

#### メタデータテーブル
- **entity_meta**: エンティティタイプの定義（人員、デバイス等）
- **attribute_meta**: 属性タイプの定義（氏名、メール、シリアル番号等）
- **relation_meta**: リレーションタイプの定義（使用中、インストール済み等）

#### データテーブル
- **entity**: 実際のエンティティインスタンス
- **attribute**: 実際の属性値
- **relation**: 実際のリレーションシップ

#### 特徴
- **時系列対応**: 登録日、無効化日、イベント日で時間軸を管理
- **柔軟性**: メタデータを変更することで新しいエンティティタイプや属性を動的に追加可能
- **整合性**: 外部キー制約でデータの整合性を保証

### サンプルデータ

#### エンティティタイプ
- **人員**: 田中太郎（営業部主任）、佐藤花子（開発部エンジニア）
- **デバイス**: ThinkPad X1、MacBook Pro
- **ソフトウェア**: Microsoft Office、Adobe Creative Suite
- **オフィス機器**: プリンター01

#### リレーション例
- 田中太郎 → **使用中** → ThinkPad X1
- 佐藤花子 → **使用中** → MacBook Pro
- 田中太郎 → **インストール済み** → Microsoft Office
- ThinkPad X1 → **搭載ソフトウェア** → Microsoft Office

## APIエンドポイント

### 統計情報
GET `/api/dashboard-stats`

レスポンス例:
```json
{
  "staff": 2,
  "devices": 2,
  "software": 2,
  "office": 1
}
```

### 最近のエンティティ
GET `/api/recent-entities`

レスポンス例:
```json
[
  {
    "identifier": 7,
    "title": "プリンター01",
    "date_in": "2022-12-01",
    "type_name": "オフィス機器"
  }
]
```

| 変数名 | 必須 | 説明 |
|--------|------|------|
| `SECRET_KEY` | はい | Flaskセッションの暗号化キー |
| `OIDC_METADATA_URL` | はい | OIDCプロバイダーのメタデータURL |
| `OIDC_CLIENT_ID` | はい | OIDCクライアントID |
| `OIDC_CLIENT_SECRET` | はい | OIDCクライアントシークレット |
| `OIDC_SCOPE` | いいえ | 要求するスコープ（デフォルト: openid profile email） |
| `OIDC_PROVIDER_NAME` | いいえ | 表示用のプロバイダー名（デフォルト: OIDC Provider） |

## 主要な機能

### 認証フロー
1. ユーザーがログインを要求
2. OIDCプロバイダーの認証画面にリダイレクト
3. ユーザーが認証情報を入力
4. プロバイダーから認可コードを受け取り
5. アクセストークンを取得してユーザー情報を抽出
6. セッションに保存してログイン完了

### アクセス制御
- 保護されたページはセッションの有無をチェック
- 未認証の場合は自動的にホームページにリダイレクト
- フラッシュメッセージでユーザーに状態を通知

## カスタマイズ

### 追加のスコープを要求する場合

```env
OIDC_SCOPE=openid profile email groups roles
```

### カスタムユーザー情報の取得

`get_user_info()`関数を修正して、追加のユーザー属性を取得：

```python
def get_user_info(token):
    try:
        userinfo = token.get('userinfo')
        if userinfo:
            return {
                'id': userinfo.get('sub'),
                'name': userinfo.get('name') or userinfo.get('preferred_username'),
                'email': userinfo.get('email'),
                'picture': userinfo.get('picture'),
                'groups': userinfo.get('groups', []),  # 追加
                'roles': userinfo.get('roles', [])     # 追加
            }
    except Exception as e:
        print(f"Error getting user info: {e}")
        return None
    return None
```

## セキュリティ上の注意

- **本番環境では適切な`SECRET_KEY`を設定**
- **HTTPS環境での運用を推奨**
- **適切な認証済みリダイレクトURIの設定**
- **環境変数ファイル（`.env`）をバージョン管理に含めない**
- **Client Secretは安全に管理し、外部に漏れないよう注意**

## トラブルシューティング

### よくある問題

1. **redirect_uri_mismatch エラー**
   - OIDCプロバイダーで正しいリダイレクトURIが設定されているか確認
   - `http://localhost:5000/authorize`が登録されているか確認

2. **invalid_client エラー**
   - `OIDC_CLIENT_ID`と`OIDC_CLIENT_SECRET`が正しく設定されているか確認
   - プロバイダーでクライアントが有効になっているか確認

3. **metadata取得エラー**
   - `OIDC_METADATA_URL`が正しく設定されているか確認
   - プロバイダーのメタデータエンドポイントにアクセス可能か確認

4. **セッションエラー**
   - `SECRET_KEY`が設定されているか確認
   - セッションcookieが有効になっているか確認

### デバッグ方法

デバッグモードを有効にして詳細なログを確認：

```python
# app.pyの最後の行を以下に変更
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
```

## 拡張アイデア

### 認証機能の拡張
- 役割ベースのアクセス制御（RBAC）
- API認証機能の追加
- 多要素認証（MFA）の統合
- 管理者用ダッシュボード
- ユーザー管理機能

### 資産管理機能の拡張
- **CRUD操作**: エンティティの作成、編集、削除機能
- **一括インポート**: CSV/Excelファイルからのデータインポート
- **レポート機能**: 資産レポートの生成とエクスポート
- **監査ログ**: 全操作の詳細なログ記録
- **アラート機能**: 契約期限切れやメンテナンス期限の通知
- **QRコード**: 物理資産へのQRコードラベル印刷
- **承認ワークフロー**: 資産の貸出・返却の承認プロセス
- **カテゴリ管理**: より詳細なカテゴリ分類
- **場所管理**: オフィスや部屋単位での資産配置管理
- **コスト管理**: 購入価格、減価償却、維持費用の管理
- **ベンダー管理**: 供給業者や保守業者の管理
- **契約管理**: ライセンス契約や保守契約の管理
- **バックアップ・復元**: データのバックアップと復元機能
- **API拡張**: RESTful APIの充実
- **モバイル対応**: スマートフォン・タブレット向けUI
- **グラフ・チャート**: 可視化機能の強化
- **検索の高度化**: 全文検索、複合条件検索
- **通知システム**: メール・Slack等への通知連携

### システム全体の改善
- PostgreSQL/MySQL対応（大規模運用）
- Redis等のキャッシュシステム統合
- Docker対応とKubernetes展開
- CI/CDパイプライン構築
- 自動テスト（単体テスト、統合テスト）
- パフォーマンス監視
- セキュリティ強化（CSP、CSRF対策等）
- 国際化対応（多言語サポート）

## まとめ

このアプリケーションは、モダンな認証機能と柔軟な資産管理システムを組み合わせた、企業や組織のデジタルトランスフォーメーションを支援するプラットフォームです。

### 主な特徴
- **ゼロコンフィグュレーション**: 初回起動時にデータベースとサンプルデータが自動設定
- **柔軟性**: メタデータドリブン設計で新しいエンティティタイプを動的に追加可能
- **汎用性**: あらゆるOIDCプロバイダーと連携可能
- **スケーラビリティ**: 小規模から始めて必要に応じて拡張可能
- **セキュリティ**: 業界標準のOIDC認証で安全なアクセス制御
- **独立性**: 外部CSS/JSフレームワークに依存しない軽量設計
- **PC最適化**: デスクトップブラウザ専用の安定したUI

### 適用事例
- 中小企業のIT資産管理
- スタートアップの成長期資産管理
- 教育機関の機器管理
- 非営利団体のリソース管理
- プロジェクトベースの一時的資産管理

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
