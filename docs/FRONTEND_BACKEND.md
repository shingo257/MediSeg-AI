# フロントエンド・バックエンド連携ガイド

MediSeg.AI の Web GUI は、React（Vite）フロントエンドと Flask バックエンドで構成されています。開発時と本番相当の動かし方をまとめます。

## 開発時（フロントとバックを別プロセスで動かす）

1. **バックエンド（Flask）を起動**
   ```bash
   python main.py gui --type web
   ```
   - デフォルトで `http://127.0.0.1:8080` で待ち受けます。
   - ホスト/ポートは環境変数 `MEDISEG_HOST` / `MEDISEG_PORT` で変更可能（詳細は [USAGE.md](../USAGE.md) 参照）。

2. **フロントエンド（Vite）を起動**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - デフォルトで `http://localhost:3000` で開発サーバーが立ち上がります。
   - Vite のプロキシ設定により、`/api` へのリクエストは `http://localhost:8080` に転送されます（[frontend/vite.config.ts](../frontend/vite.config.ts) の `server.proxy`）。

3. **利用手順**
   - ブラウザでは **http://localhost:3000** にアクセスしてフロントを利用します。
   - フロントから呼ばれる API は自動的にバックエンド（8080）にプロキシされます。

## 本番相当（フロントをビルドしてバックエンドから配信）

1. **フロントエンドをビルド**
   ```bash
   cd frontend
   npm run build
   ```
   - ビルド成果物は `backend/gui/web/static` に出力されます（`vite.config.ts` の `build.outDir`）。

2. **バックエンドのみ起動**
   ```bash
   python main.py gui --type web
   ```
   - Flask が `templates/` と `backend/gui/web/static` を参照し、同一オリジンでフロント＋API を提供します。
   - ブラウザでは **http://127.0.0.1:8080**（または設定したホスト/ポート）にアクセスします。
   - ルート (`/`) および `/dashboard`, `/segmentation` などのクライアント側ルートは、ビルド済みの React SPA の `index.html` を返します（`backend/gui/web/static/index.html` が存在する場合）。静的アセットは `/static/` から配信されます。

## 接続まわり

- **開発時**: フロント (3000) → プロキシ `/api` → バックエンド (8080)。API のベース URL はフロントから見て `/api` のままです。
- **本番相当**: フロントもバックエンドも同じオリジン（例: 8080）なので、API は同じホストの `/api` でそのまま利用できます。

環境変数（`MEDISEG_HOST`, `MEDISEG_PORT` など）の詳細は [USAGE.md](../USAGE.md) を参照してください。
