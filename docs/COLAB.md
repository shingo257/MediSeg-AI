# Google Colab で MediSeg.AI を動かす

Google Colaboratory の無料GPUで、MediSeg.AI のデモ・Web GUI・学習を実行する手順です。

- **学習（訓練）を Colab で行う**: [COLAB_TRAINING_GUIDE.md](COLAB_TRAINING_GUIDE.md) に具体的な手順とデータセットのダウンロード可否をまとめています。

---

## 1. ノートブックを開く

- **GitHub から**: リポジトリの [`MediSeg_AI_Colab.ipynb`](../MediSeg_AI_Colab.ipynb) を開き、**「Open in Colab」** をクリックするか、
- **Colab にアップロード**: [Google Colab](https://colab.research.google.com) にログインし、`MediSeg_AI_Colab.ipynb` をアップロードして開く。

---

## 2. 最小手順（とりあえず動かす）

1. **ランタイム > ランタイムのタイプを変更** で **GPU** を選択（任意・推奨）。
2. **セル 1（クローン）**: `REPO_URL` を **自分のリポジトリURL** に書き換える（フォークした場合はそのURL）。  
   例: `https://github.com/あなたのユーザー名/MediSeg-AI.git`
3. **セル 2（クローン実行）** を実行 → リポジトリが `/content/MediSeg-AI` にクローンされる。
4. **セル 3（セットアップ）** を実行 → `pip install` とディレクトリ作成が行われる。
5. **セル 4（Web GUI 起動）** を実行 → 表示された URL（`http://127.0.0.1:8080` または ngrok のURL）をブラウザで開く。

**注意**: Web GUI を表示しているセルは **実行し続けたまま** にしておく必要があります。セル実行を止めるとサーバーも止まります。

---

## 3. よく使う操作

### デモの実行（データ不要）

ノートブック内の「学習を実行する」セルで次を実行します。

```bash
!python main.py demo
```

### 学習の実行（合成データ）

1. 合成データを生成してから `train-medical` を実行します。

```python
from mediseg_ai.data_loaders.real_datasets import RealDatasetDownloader
d = RealDatasetDownloader(data_dir="/content/MediSeg-AI/data")
d.download_dataset("medical_small")
```

```bash
!python main.py train-medical --data-dir /content/MediSeg-AI/data/medical_small --save-dir /content/MediSeg-AI/results
```

### 外部から Web GUI にアクセス（ngrok）

- [ngrok](https://dashboard.ngrok.com/signup) で無料アカウントを作成し、[認証トークン](https://dashboard.ngrok.com/get-started/your-authtoken) を取得する。
- ノートブックの「ngrok認証トークンの設定」セルで `NGROK_TOKEN = "あなたのトークン"` を設定する。
- Web GUI 起動セルを実行すると、ngrok の公開URLが表示される。

---

## 4. トラブルシューティング

| 現象 | 対処 |
|------|------|
| `ModuleNotFoundError: No module named 'backend'` | セル 3 で `sys.path.insert(0, REPO_DIR)` と `!python colab_setup.py` を実行したか確認。先にセル 2・3 を順に実行する。 |
| GPU が使えない | **ランタイム > ランタイムのタイプを変更 > GPU** を選び、ランタイムを再起動する。 |
| Web GUI の URL にアクセスできない | Colab 上では「プレビュー」リンクを使うか、ngrok トークンを設定して表示された公開URLを使う。 |
| セッションが切れた | 無料枠は約12時間でタイムアウトします。必要なファイルは Google Drive に保存しておく。 |

---

## 5. 関連ドキュメント

- [USAGE.md](../USAGE.md) - ローカルでの起動・コマンド一覧
- [docs/TRAINING_COST_COMPARISON.md](TRAINING_COST_COMPARISON.md) - 手持ちPC vs クラウドのコスト比較
