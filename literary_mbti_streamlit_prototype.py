# literary_mbti_streamlit_prototype.py
# "文学 MBTI" 问卷的 Streamlit 网页应用原型 — 单文件版本
# 运行方式: streamlit run literary_mbti_streamlit_prototype.py

import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="文学 MBTI 测试", layout="centered")

# ----------
# 配置：请将这些数据替换为你的实际数据
# ----------

# 示例问题格式：
# 每个问题必须包含：id, text, axis (其中一个是 'EI','SN','TF','JP')
# 以及选项：(label, value) 列表，其中 value 是贡献给该维度的一个字母（例如 'E' 或 'I'）
QUESTIONS = [
    {"id": 1, "text": "我更喜欢在聚会中与很多人交谈，而不是和一个人深入交谈。", "axis": "EI", "options": [("更喜欢多人与人互动", "E"), ("更喜欢与少数人深入交谈", "I")]},
    {"id": 2, "text": "读小说时，我更关注人物内心世界的复杂情感，而不是事件的外在发展。", "axis": "SN", "options": [("关注情节与事实", "S"), ("关注人物内心与象征", "N")]},
    {"id": 3, "text": "在读书或写作中，我倾向于用逻辑和结构来分析，而不是依赖直觉和感受。", "axis": "TF", "options": [("倾向逻辑分析", "T"), ("依赖情感与价值", "F")]},
    {"id": 4, "text": "我偏好有计划、有条理的阅读/写作习惯，而不是临时决定要做什么。", "axis": "JP", "options": [("有计划", "J"), ("随性", "P")]},
]

# MBTI 类型描述和推荐书籍示例
# 键是 MBTI 代码，如 'ENFP'
MBTI_PROFILES = {
    "ENFP": {
        "title": "热情的想象者（ENFP）",
        "description": "倾向直觉与情感，喜欢探索人物心灵与可能性。适合富有想象力、情节浪漫或意识流的文学。",
        "books": ["《百年孤独》 - 加西亚·马尔克斯", "《挪威的森林》 - 村上春树"]
    },
    "ISTJ": {
        "title": "严谨的记录者（ISTJ）",
        "description": "偏好细节与秩序，喜欢情节严谨、结构清晰的现实题材作品。",
        "books": ["《局外人》 - 加缪", "《人类群星闪耀时》 - 斯蒂芬·茨威格"]
    },
    # ... add all 16 profiles
}

# ----------
# 辅助函数
# ----------

def compute_mbti(answers):
    # answers: dict 问题ID -> 选择的值 (一个字母)
    axis_map = {"EI": {"E": 0, "I": 0}, "SN": {"S": 0, "N": 0}, "TF": {"T": 0, "F": 0}, "JP": {"J": 0, "P": 0}}
    for q in QUESTIONS:
        qid = q['id']
        axis = q['axis']
        val = answers.get(str(qid))
        if val in axis_map[axis]:
            axis_map[axis][val] += 1
    # 构建 MBTI 类型
    mbti = ''
    # 平局决胜规则：选择第一个键 (E 优于 I, S 优于 N, T 优于 F, J 优于 P)
    mbti += 'E' if axis_map['EI']['E'] >= axis_map['EI']['I'] else 'I'
    mbti += 'S' if axis_map['SN']['S'] >= axis_map['SN']['N'] else 'N'
    mbti += 'T' if axis_map['TF']['T'] >= axis_map['TF']['F'] else 'F'
    mbti += 'J' if axis_map['JP']['J'] >= axis_map['JP']['P'] else 'P'
    return mbti, axis_map


# ----------
# 用户界面：问卷
# ----------

st.title("文学 MBTI 快速测评")
st.write("请在下方回答以下问题（适配手机浏览器，简单直接）。")

with st.form(key='mbti_form'):
    answers = {}
    for q in QUESTIONS:
        cols = st.columns([1, 2])
        st.write(f"**{q['id']}. {q['text']}**")
        # 渲染单选按钮
        options_labels = [opt[0] for opt in q['options']]
        options_values = [opt[1] for opt in q['options']]
        choice_index = st.radio(label=f"", options=list(range(len(options_labels))), format_func=lambda i: options_labels[i], key=f"q{q['id']}")
        answers[str(q['id'])] = options_values[choice_index]
        st.markdown("---")
    submitted = st.form_submit_button("提交并查看结果")

if submitted:
    mbti, breakdown = compute_mbti(answers)
    st.subheader(f"你的文学 MBTI：{mbti}")

    # 显示各维度分析
    st.write("**各维度计分**")
    df = pd.DataFrame([{
        '维度': '外向 vs 内向 (E/I)', 'E': breakdown['EI']['E'], 'I': breakdown['EI']['I']
    },{
        '维度': '感觉 vs 直觉 (S/N)', 'S': breakdown['SN']['S'], 'N': breakdown['SN']['N']
    },{
        '维度': '思考 vs 情感 (T/F)', 'T': breakdown['TF']['T'], 'F': breakdown['TF']['F']
    },{
        '维度': '判断 vs 感知 (J/P)', 'J': breakdown['JP']['J'], 'P': breakdown['JP']['P']
    }])
    st.dataframe(df)

    profile = MBTI_PROFILES.get(mbti)
    if profile:
        st.write(f"### {profile['title']}")
        st.write(profile['description'])
        st.write("**推荐书目：**")
        for b in profile['books']:
            st.write(f"- {b}")
    else:
        st.write("抱歉，还没有该 MBTI 的详细资料。你可以把你的结果发给我，我可以帮你手工匹配推荐书目。")

    # 可选：将结果保存到 CSV 文件
    save = st.checkbox("保存我的答题记录到服务器（仅用于示例，保存在本地CSV）")
    if save:
        row = {
            'timestamp': datetime.utcnow().isoformat(),
            'mbti': mbti,
            'answers': json.dumps(answers, ensure_ascii=False)
        }
        df_row = pd.DataFrame([row])
        try:
            df_row.to_csv('responses.csv', mode='a', header=not st.experimental_get_query_params().get('hdr'), index=False)
            st.success('已保存到 responses.csv')
        except Exception as e:
            st.error(f'保存失败: {e}')

# ----------
# 说明（应用内）
# ----------

st.sidebar.header('说明与部署')
st.sidebar.markdown(
"""
1. 本原型为单文件 Streamlit 应用。运行: `streamlit run literary_mbti_streamlit_prototype.py`。
2. 把 QUESTIONS 替换为你自己的题库；每题的 `axis` 用 'EI','SN','TF','JP'。
3. 把 MBTI_PROFILES 填全 16 个类型的描述与书单。
4. 部署: 可直接把文件上传到 Streamlit Cloud（https://share.streamlit.io）或用 Heroku/Render。
5. 手机上打开部署后的链接即可答题，过程简单友好。
"""
)
