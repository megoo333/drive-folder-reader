# drive-folder-reader

Google Driveの授業フォルダ構成を読み取るための最小Pythonリポジトリです。

この最初の版ではGoogle Drive APIには接続しません。Google Driveから取得した想定のサンプルJSONを読み込み、科目フォルダ、回数フォルダ、資料ファイルを整理して出力します。

## できること

- Drive風のJSONからフォルダとファイルを読み取る
- 科目フォルダを抽出する
- 回数フォルダを `1`, `2`, `10`, `第10回` などから判定する
- 各回フォルダ内の資料ファイルをまとめる
- 科目直下にある共通資料もまとめる
- 結果をPythonの辞書またはJSONとして出力する

## ディレクトリ構成

```text
drive-folder-reader/
├── README.md
├── sample.py
├── samples/
│   └── sample_drive_items.json
└── src/
    └── drive_folder_reader.py
```

## 使い方

```bash
cd drive-folder-reader
python3 sample.py
```

## 入力JSONの形式

```json
{
  "files": [
    {
      "id": "folder-design",
      "title": "デザインスキル（design skill)",
      "mime_type": "application/vnd.google-apps.folder",
      "url": "https://drive.google.com/drive/folders/folder-design",
      "parent_id": null
    }
  ]
}
```

必須項目:

- `id`
- `title`
- `mime_type`

任意項目:

- `url`
- `parent_id`

## 出力例

```json
{
  "subjects": [
    {
      "id": "folder-design",
      "title": "デザインスキル（design skill)",
      "lessons": [
        {
          "lesson_number": 10,
          "title": "10",
          "materials": [
            {
              "title": "デザインスキル応用_第10回_スマホ対応",
              "type": "presentation"
            }
          ]
        }
      ],
      "shared_materials": []
    }
  ]
}
```

## 次に拡張できること

- Google Drive APIから実データを取得する
- 階層が深いフォルダにも対応する
- ファイル種別ごとの集計を増やす
- 授業回の日付やテーマを推定する
- 結果をMarkdownやCSVで出力する
