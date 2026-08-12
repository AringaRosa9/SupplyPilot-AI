# SupplyPilot AI

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

グローバル旅行 EC 向けに、サプライヤー開拓の自動化、商品評価、在庫ポートフォリオの意思決定を支援する AI プラットフォームです。

SupplyPilot AI は、マーケティングキャンペーンの開始、調達タスクの分解、商品の登録と自動検証、商品評価、在庫プール管理から、供給ギャップの特定、サプライヤーリスクの警告、商品ラインの振り返りまで、業務全体をカバーします。本プロジェクトは、データにチャット機能を追加するだけでなく、AI エージェント、説明可能なスコアリングモデル、イベント駆動型オートメーションをサプライチェーンのワークフローへ直接組み込む方法を示します。

> 現在の段階：M0 の設計確定とエンジニアリング基盤が完了しました。次の M1 では、デモデータとプロダクトの基本 UI を構築します。

## 主なユースケース

「東南アジア夏季旅行フェスティバル」を例に、システムは次の処理を実行できます。

1. 自然言語で記述されたキャンペーン要件を、構造化された調達条件へ変換する。
2. 対象市場、ホテルカテゴリ、航空路線ごとの供給ギャップを特定する。
3. Hotel と Flight の商品ライン向け調達タスクを自動生成し、担当者へ割り当てる。
4. サプライヤーが登録した価格、在庫、キャンペーン適合性を検証する。
5. 商品ライン別モデルで商品を評価し、信頼度と根拠を提示する。
6. 在庫プールの健全性とサプライヤー集中度を監視し、追加調達アラートを発行する。
7. 商品掲載とフロント画面での表示順位を提案する。
8. キャンペーン終了後に、商品ラインとサプライヤーの振り返りレポートを生成する。

## プロダクト機能

- キャンペーンと調達タスクの協働管理
- AI による調達要件の構造化
- 商品の一括登録と自動検証
- 在庫プールのライフサイクル全体の管理
- Hotel / Flight 向けの説明可能な評価モデル
- Product Line Intelligence Agent
- 供給ギャップ、集中度、在庫健全性の分析
- イベント駆動型の自動化ルールとアラート
- キャンペーン横断の商品ラインおよびサプライヤー評価

## MVP の範囲

第 1 フェーズでは Hotel と Flight の 2 商品ラインに注力し、デモ可能なエンドツーエンドの業務フローを実現します。

```text
キャンペーン作成 → 調達タスク分解 → 商品インポート → 自動検証 → 商品評価
                 → 手動レビュー → 掲載提案 → 供給分析 → キャンペーン振り返り
```

MVP には、キャンペーン管理、CSV インポート、ルール検証、2 種類のスコアリングモデル、在庫プールのダッシュボード、供給分析、エージェントによるデータ Q&A、自動アラート、再現可能な合成データを含みます。

## 技術アーキテクチャ

| レイヤー | 技術 |
|---|---|
| Web | Next.js、TypeScript、Tailwind CSS。グラフ機能では ECharts を導入予定 |
| API | FastAPI、Pydantic、SQLAlchemy 2、Alembic |
| データベース | PostgreSQL 16 |
| 非同期ジョブ | Redis、Celery |
| データ分析 | SQL、必要に応じて Polars |
| AI | LLM Tool Calling、制御された分析ツール、オプションの RAG |
| デリバリー | Docker Compose、自動テスト、GitHub Actions |

アーキテクチャ原則：評価結果の説明可能性、モデルとルールのバージョン管理、エージェント操作の制御、重要な変更の確認、自動状態変更の監査可能性を重視します。詳細は[システムアーキテクチャ](docs/architecture.md)を参照してください。

## リポジトリ構成

```text
supplypilot-ai/
├── README.md
├── README.en.md
├── README.ja.md
├── CONTRIBUTING.md
├── .gitignore
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   ├── scoring-model.md
│   ├── agent-design.md
│   ├── data-dictionary.md
│   └── demo-script.md
├── frontend/             # Next.js Web アプリと基盤コンポーネント
├── backend/              # FastAPI、Celery、SQLAlchemy、マイグレーション
├── docker-compose.yml
├── Makefile
├── data/
│   └── README.md
└── notebooks/
    └── README.md
```

## ドキュメント

- [プロダクト要件](docs/PRD.md)
- [フロントエンドの画面・レイアウト設計](docs/frontend-design.md)
- [MVP 開発計画](docs/development-plan.md)
- [システムアーキテクチャ](docs/architecture.md)
- [商品スコアリングモデル](docs/scoring-model.md)
- [エージェント設計](docs/agent-design.md)
- [データ辞書](docs/data-dictionary.md)
- [デモスクリプト](docs/demo-script.md)
- [コントリビューションガイド](CONTRIBUTING.md)

M0 では、システムアーキテクチャ、データ状態、スコアリングモデル、エージェントの境界を確定しました。今後のマイルストーンでは、これらの契約を基盤として開発を進めます。

## ローカルでの起動

環境変数ファイルをコピーし、すべてのサービスを起動します。

```bash
cp .env.example .env
docker compose up --build
```

- Web：<http://localhost:3000>
- API ヘルスチェック：<http://localhost:8000/api/v1/health>
- OpenAPI：<http://localhost:8000/api/docs>

ローカル品質チェックは `make check` で実行できます。初回セットアップ時は、`backend/README.md` と `frontend/README.md` の手順に従って開発用依存関係をインストールしてください。

## マイルストーン

- [x] プロジェクトの位置付けと名称を決定
- [x] 初版 PRD を作成
- [x] ドキュメントとエンジニアリングの骨格を構築
- [x] 情報アーキテクチャ、データモデル、システムアーキテクチャを完成
- [ ] 再現可能な合成データセットを準備
- [ ] キャンペーン、調達タスク、在庫プールの基本フローを実装
- [ ] Hotel / Flight の評価エンジンを実装
- [ ] 供給インテリジェンス、自動化ルール、エージェントを実装
- [ ] テスト、Docker 化、デモ動画、プロジェクト振り返りを完成

## プロジェクト状況

SupplyPilot AI は M0 を完了しています。[PRD](docs/PRD.md)をプロダクト範囲の基準とし、技術・業務契約の変更は ADR、マイグレーション、対応するテストに記録します。
