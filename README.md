# Todo-App

![todo](https://github.com/user-attachments/assets/5462da8c-cfd9-428f-bd00-c72b7cc87ebb)

# Technology used

### front-end

- React(TypeScript)

### back-end

- Flask(Python)

### database

- SQLite

# Points

- ログイン機能

  - username と password による認証
  - password は[SHA-256](https://academo.org/demos/SHA-256-hash-generator/)によりハッシュ化することでセキュリティリスクを下げている
  - [generate_password_hash](https://werkzeug.palletsprojects.com/en/2.3.x/utils/#werkzeug.security.generate_password_hash)などで実現

- ロード中にスピナーを表示

  - UX 向上
  - CSS で実現

- ページをリロードするごとに、input 欄に focus があたる

  - 登録ボタンを押した後も focus が input 欄に戻る
  - useRef, autofocus 属性で実現

- エラーハンドリングを実装

  - try ~ catch ~ 構文などで実現

- UI 改善

  - CSS, [React Icons](https://react-icons.github.io/react-icons/), [react-hot-toast](https://react-hot-toast.com/)により実現

- テストコードを実装

  - frontend(11 test)

    - frontend/ディレクトリでターミナルを開き、用途別に以下から選んで実行
      - `npm run test`
      - `npm run coverage`
    - [Vitest](https://vitest.dev/)で実現

  - backend(13 test)
    - backend/ディレクトリでターミナルを開き、用途別に以下から選んで実行
      - `pytest`
      - `pytest --cov=app tests/`
      - `pytest --cov=app --cov-report=html tests/`
    - [pytest](https://docs.pytest.org/en/stable/)で実現

- コードスタイルのチェック
  - [pylint](https://pypi.org/project/pylint/)で実現
    - backend/ディレクトリで`pylint app.py`実行

# How to use

1. backend server を立ち上げる

backend/ディレクトリでターミナルを開き、以下を実行

```bash
python app.py
```

2. frontend server を立ち上げる

frontend/ディレクトリでターミナルを開き、以下を実行

```bash
npm run dev
```

3. database を確認する(option)

backend/instance ディレクトリでターミナルを開き、

```bash
sqlite3 my_database.db
```

を実行する。そして

```sql
.tables
```

を実行して todo テーブルと user テーブルがあることを確認する。<br>
そしてそれぞれのテーブルの中身を確認する SQL コマンドは以下。

```sql
SELECT * FROM todo;
SELECT * FROM user;
```

# Upcoming

[issue](https://github.com/clumsy-ug/Todo-Fullstack/issues)を参照
