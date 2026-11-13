"""プロ検クラス向け 3択クイズ Webアプリ（Streamlit）"""
import json
import random
import streamlit as st

st.set_page_config(page_title="みんなの3択クイズ", page_icon="🎯", layout="centered")

DEFAULT_QUESTIONS = [
    {"question": "日本で一番高い山は？", "choices": ["富士山", "北岳", "槍ヶ岳"], "answer": 0},
    {"question": "Pythonで文字を表示する命令は？", "choices": ["input()", "print()", "len()"], "answer": 1},
    {"question": "7 × 8 は？", "choices": ["54", "56", "64"], "answer": 1},
    {"question": "Pythonで関数を定義するときに使うのは？", "choices": ["def", "if", "for"], "answer": 0},
    {"question": "1時間は何分？", "choices": ["30分", "60分", "100分"], "answer": 1},
]


def validate_questions(data):
    if not isinstance(data, list) or len(data) > 200:
        raise ValueError("問題データは200問以内のリストにしてください。")
    validated = []
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{i}問目の形式が正しくありません。")
        q, choices, answer = item.get("question"), item.get("choices"), item.get("answer")
        if not isinstance(q, str) or not q.strip() or len(q) > 300:
            raise ValueError(f"{i}問目の問題文を確認してください。")
        if not isinstance(choices, list) or len(choices) != 3 or any(
            not isinstance(c, str) or not c.strip() or len(c) > 150 for c in choices
        ):
            raise ValueError(f"{i}問目の選択肢は3つ必要です。")
        if type(answer) is not int or answer not in (0, 1, 2):
            raise ValueError(f"{i}問目の正解番号は0〜2にしてください。")
        validated.append({"question": q.strip(), "choices": [c.strip() for c in choices], "answer": answer})
    return validated


def reset_quiz():
    st.session_state.order = []
    st.session_state.position = 0
    st.session_state.score = 0
    st.session_state.selected = None
    st.session_state.quiz_questions = []
    st.session_state.page = "home"


if "questions" not in st.session_state:
    st.session_state.questions = [dict(q) for q in DEFAULT_QUESTIONS]
if "page" not in st.session_state:
    reset_quiz()

st.title("🎯 みんなの3択クイズ")
st.caption("自分で問題を作って、友だちや家族に挑戦してもらおう！")

with st.sidebar:
    st.header("メニュー")
    if st.button("🏠 ホーム", use_container_width=True):
        reset_quiz()
        st.rerun()
    if st.button("✏️ 問題を作る・編集", use_container_width=True):
        st.session_state.page = "edit"
        st.rerun()
    if st.button("📁 保存・読み込み", use_container_width=True):
        st.session_state.page = "files"
        st.rerun()
    st.caption("問題は現在の画面内に一時保存されます。消える前にJSONをダウンロードしてください。")

page = st.session_state.page

if page == "home":
    st.subheader("クイズに挑戦！")
    count = len(st.session_state.questions)
    st.write(f"現在 **{count}問** 登録されています。")
    if count:
        number = st.slider("何問出題する？", 1, count, min(5, count))
        shuffle = st.checkbox("問題をランダムに出す", value=True)
        if st.button("▶ クイズスタート", type="primary", use_container_width=True):
            st.session_state.quiz_questions = [dict(q) for q in st.session_state.questions]
            order = list(range(count))
            if shuffle:
                random.shuffle(order)
            st.session_state.order = order[:number]
            st.session_state.position = 0
            st.session_state.score = 0
            st.session_state.selected = None
            st.session_state.page = "quiz"
            st.rerun()
    else:
        st.info("問題がありません。『問題を作る・編集』から追加してください。")

elif page == "quiz":
    pos = st.session_state.position
    order = st.session_state.order
    if pos >= len(order):
        st.session_state.page = "result"
        st.rerun()
    q = st.session_state.quiz_questions[order[pos]]
    st.progress(pos / len(order))
    st.write(f"**第 {pos + 1} 問 / {len(order)} 問**　　正解数：{st.session_state.score}")
    st.subheader(q["question"])
    for i, choice in enumerate(q["choices"]):
        if st.button(f"{i+1}. {choice}", key=f"choice_{pos}_{i}", use_container_width=True,
                     disabled=st.session_state.selected is not None):
            st.session_state.selected = i
            if i == q["answer"]:
                st.session_state.score += 1
            st.rerun()
    if st.session_state.selected is not None:
        if st.session_state.selected == q["answer"]:
            st.success("⭕ 正解！")
        else:
            st.error(f"❌ 残念！ 正解は「{q['choices'][q['answer']]}」です。")
        if st.button("結果を見る" if pos + 1 == len(order) else "次の問題へ →", type="primary", use_container_width=True):
            st.session_state.position += 1
            st.session_state.selected = None
            st.rerun()

elif page == "result":
    total = len(st.session_state.order)
    score = st.session_state.score
    if total > 0 and score == total:
        st.balloons()
    st.subheader("🏆 結果発表！")
    st.metric("正解数", f"{score} / {total}")
    st.write("すばらしい！" if score == total else "もう一度挑戦してみよう！")
    if st.button("🔁 もう一度遊ぶ", type="primary", use_container_width=True):
        reset_quiz()
        st.rerun()

elif page == "edit":
    st.subheader("✏️ 問題を作る")
    with st.form("add_question", clear_on_submit=True):
        question = st.text_input("問題文", max_chars=300)
        c1 = st.text_input("選択肢1", max_chars=150)
        c2 = st.text_input("選択肢2", max_chars=150)
        c3 = st.text_input("選択肢3", max_chars=150)
        answer = st.radio("正解はどれ？", [1, 2, 3], horizontal=True)
        submitted = st.form_submit_button("問題を追加", type="primary")
        if submitted:
            if not all(x.strip() for x in (question, c1, c2, c3)):
                st.warning("問題文と選択肢をすべて入力してください。")
            elif len(st.session_state.questions) >= 200:
                st.warning("登録できるのは200問までです。")
            else:
                st.session_state.questions.append({"question": question.strip(), "choices": [c1.strip(), c2.strip(), c3.strip()], "answer": answer - 1})
                st.success("問題を追加しました！")
    st.divider()
    st.subheader(f"登録済みの問題（{len(st.session_state.questions)}問）")
    for i, q in enumerate(st.session_state.questions):
        with st.expander(f"{i+1}. {q['question']}"):
            with st.form(f"edit_{i}"):
                eq = st.text_input("問題文", q["question"], key=f"eq_{i}")
                ec = [st.text_input(f"選択肢{j+1}", q["choices"][j], key=f"ec_{i}_{j}") for j in range(3)]
                ea = st.radio("正解", [1, 2, 3], index=q["answer"], horizontal=True, key=f"ea_{i}")
                if st.form_submit_button("変更を保存"):
                    if all(x.strip() for x in [eq, *ec]):
                        st.session_state.questions[i] = {"question": eq.strip(), "choices": [x.strip() for x in ec], "answer": ea - 1}
                        st.rerun()
                    else:
                        st.warning("空欄は保存できません。")
            if st.button("この問題を削除", key=f"delete_{i}"):
                st.session_state.questions.pop(i)
                st.rerun()

elif page == "files":
    st.subheader("📁 問題の保存・読み込み")
    st.info("問題は自動的には永続保存されません。終了前にダウンロードしてください。")
    data = json.dumps(st.session_state.questions, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button("⬇ 問題をJSONファイルに保存", data=data, file_name="quiz_questions.json", mime="application/json", use_container_width=True)
    uploaded = st.file_uploader("保存したJSONファイルを読み込む", type=["json"])
    if uploaded is not None and st.button("このファイルの問題に入れ替える", type="primary"):
        try:
            loaded = json.loads(uploaded.getvalue().decode("utf-8-sig"))
            st.session_state.questions = validate_questions(loaded)
            st.success(f"{len(loaded)}問を読み込みました。")
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
            st.error(f"読み込みに失敗しました：{e}")
