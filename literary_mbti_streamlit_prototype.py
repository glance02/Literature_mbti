# literary_mbti_streamlit_full.py
# Streamlit app for "文学 MBTI" questionnaire with full questions and 16 profiles
# Run: streamlit run literary_mbti_streamlit_full.py

import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="文学 MBTI 测试", layout="centered")

# ------------------------------------
# 题目配置：来自你的 DOCX 文件（每维度 5 题）
# ------------------------------------
QUESTIONS = []

def add_questions(axis, qlist):
    for i, (text, A, B) in enumerate(qlist, 1):
        QUESTIONS.append({
            "id": f"{axis}{i}",
            "text": text,
            "axis": axis,
            "options": [(A, axis[0]), (B, axis[1])]
        })

# 焦点取向 - 情节驱动 (E) vs. 内心世界 (I)
add_questions("EI", [
    ("当你向朋友推荐一本书时，你最先描述的是什么？", "情节多么曲折离奇", "角色内心挣扎多么深刻"),
    ("什么样的冲突更能吸引你？", "外部对抗、战争或追捕", "人物内在的道德困境"),
    ("伟大小说的核心驱动力是什么？", "接下来会发生什么？", "这个人为什么会这样？"),
    ("前50页都是日常描写，你会？", "感到乏味，期待事件发生", "享受细节，理解人物生活"),
    ("你更喜欢什么样的叙事节奏？", "紧凑迅捷，信息量大", "舒缓深入，停留在情绪中"),
])

# 风格取向 - 现实主义 (S) vs. 想象主义 (N)
add_questions("SN", [
    ("什么样的新世界更让你兴奋？", "真实存在的历史时代", "完全虚构的世界"),
    ("什么样的比喻更打动你？", "常见事物的精妙类比", "抽象而富有想象力的联结"),
    ("如何看待魔法或超现实元素？", "会分散注意力", "是表达思想的隐喻工具"),
    ("阅读时，什么样的细节最让你信服？", "真实的社会细节", "虚构世界观的自洽性"),
    ("如果一本书被评价为文笔诗意，你会？", "担心矫揉造作", "期待其美感"),
])

# 决策取向 - 逻辑架构 (T) vs. 情感共鸣 (F)
add_questions("TF", [
    ("一个角色的行为，你更看重什么？", "逻辑合理", "情感冲击"),
    ("什么样的主题更能引发你的思考？", "哲学探讨", "情感命题"),
    ("如何判断反派是否成功？", "动机清晰且推动剧情", "让人理解其痛苦"),
    ("读完一本书后，你倾向讨论什么？", "叙事结构与思想", "人物命运与感受"),
    ("结局合理意味着什么？", "逻辑必然", "情感圆满"),
])

# 态度取向 - 闭合结局 (J) vs. 开放诠释 (P)
add_questions("JP", [
    ("看到幸福生活结尾，你感觉如何？", "满意安心", "想知道更多挑战"),
    ("面对可多重解读的小说，你认为？", "作者意图不清", "文学的魅力所在"),
    ("更喜欢哪种叙事结构？", "线性叙事", "碎片化多视角叙事"),
    ("结局是主角走向未知未来时，你会？", "失落，想要确定答案", "兴奋，想象各种未来"),
    ("故事结尾的作用？", "收束与交代", "开启新的思考"),
])

# ------------------------------------
# MBTI 结果数据：16型描述 + 推荐书单
# ------------------------------------
MBTI_PROFILES = {
    "ESTJ": {"title": "架构解密者", "description": "痴迷情节逻辑闭环，喜欢扎根现实、无漏洞的故事。", "books": ["《清明上河图密码》", "《东方快车谋杀案》", "《坏小孩》"]},
    "ENTJ": {"title": "世界规则掌控者", "description": "享受虚构世界的严谨逻辑，喜欢完整设定与清晰结局。", "books": ["《三体》", "《基地》", "《沙丘》"]},
    "ISTJ": {"title": "人性逻辑观察者", "description": "关注现实人物心理逻辑，人物心理转变必须符合现实逻辑。", "books": ["《活着》", "《包法利夫人》", "《人世间》"]},
    "INTJ": {"title": "隐喻逻辑解读师", "description": "喜欢虚构外壳下的心理逻辑剖析，追求隐喻与自我和解。", "books": ["《克拉拉与太阳》", "《失明症漫记》", "《蝇王》"]},
    "ESTP": {"title": "现实谜题探索者", "description": "享受现实情节的逻辑留白，通过推理探索人性。", "books": ["《白夜行》", "《局外人》", "《长夜难明》"]},
    "ENTP": {"title": "设定谜题思辨者", "description": "偏爱虚构设定的逻辑延伸，引发哲学思辨。", "books": ["《你一生的故事》", "《环形使者》", "《黑暗的左手》"]},
    "ISTP": {"title": "人性思考者", "description": "关注现实人物心理留白，通过细节引发人性思考。", "books": ["《挪威的森林》", "《斯通纳》", "《山茶文具店》"]},
    "INTP": {"title": "隐喻心理思辩者", "description": "喜欢虚构隐喻的心理留白，通过隐喻思辨内心。", "books": ["《海浪》", "《树上的男爵》", "《佩德罗·巴拉莫》"]},
    "ESFJ": {"title": "现实情感追随者", "description": "沉迷现实情节中的情感闭环，喜欢情感安放的结局。", "books": ["《平凡的世界》", "《山茶文具店》", "《夺宝奇兵》"]},
    "ENFJ": {"title": "奇幻情感守护者", "description": "享受虚构情节中的情感圆满，情感联结为核心。", "books": ["《霍比特人》", "《少年Pi的奇幻漂流》", "《星尘》"]},
    "ISFJ": {"title": "人间温情记录者", "description": "沉醉现实日常里的情感沉淀，注重生活的温情。", "books": ["《佐贺的超级阿嬷》", "《深夜食堂》", "《我们仨》"]},
    "INFJ": {"title": "奇幻心灵治愈者", "description": "偏爱虚构设定下的情感和解，看重心灵圆满。", "books": ["《小王子》", "《海洋之歌》", "《你在天堂里遇见的五个人》"]},
    "ESFP": {"title": "现实情感漫游者", "description": "享受现实情节中的情感切片，关注即时体验。", "books": ["《漫长的告别》", "《奥吉·马奇历险记》", "《飞行家》"]},
    "ENFP": {"title": "奇幻情感探索者", "description": "痴迷虚构情节中的情感可能，追求情感新鲜感。", "books": ["《银河系漫游指南》", "《爱丽丝梦游仙境》", "《夜晚的潜水艇》"]},
    "ISFP": {"title": "生活情绪捕捉者", "description": "关注现实日常里的情感余韵，细腻体验情绪。", "books": ["《古都》", "《情人》", "《秋园》"]},
    "INFP": {"title": "幻梦情感沉思者", "description": "沉醉虚构意象里的情感哲思，思考情感与思想。", "books": ["《海浪》", "《阿莱夫》", "《佩德罗·巴拉莫》"]},
}

# ------------------------------------
# 计算函数
# ------------------------------------

def compute_mbti(answers):
    axis_map = {"EI": {"E": 0, "I": 0}, "SN": {"S": 0, "N": 0}, "TF": {"T": 0, "F": 0}, "JP": {"J": 0, "P": 0}}
    for q in QUESTIONS:
        val = answers.get(q['id'])
        if val in axis_map[q['axis']]:
            axis_map[q['axis']][val] += 1
    mbti = ''.join([
        'E' if axis_map['EI']['E'] >= axis_map['EI']['I'] else 'I',
        'S' if axis_map['SN']['S'] >= axis_map['SN']['N'] else 'N',
        'T' if axis_map['TF']['T'] >= axis_map['TF']['F'] else 'F',
        'J' if axis_map['JP']['J'] >= axis_map['JP']['P'] else 'P',
    ])
    return mbti, axis_map

# ------------------------------------
# UI 部分
# ------------------------------------

st.title("📚 文学 MBTI 测试")
st.write("回答以下 20 个问题，看看你是哪种文学类型！")

with st.form(key='mbti_form'):
    answers = {}
    cnt=0;
    for q in QUESTIONS:
        cnt+=1
        st.write(f"**{cnt}.{q['text']}**")
        choice = st.radio("", [opt[0] for opt in q['options']], key=q['id'], horizontal=True)
        chosen_value = dict(q['options'])[choice]
        answers[q['id']] = chosen_value
        st.divider()
    submitted = st.form_submit_button("提交并查看结果")

if submitted:
    mbti, breakdown = compute_mbti(answers)
    st.success(f"你的文学 MBTI 类型是：**{mbti}**")

    profile = MBTI_PROFILES.get(mbti)
    if profile:
        st.header(profile['title'])
        st.write(profile['description'])
        st.write("**推荐书目：**")
        for book in profile['books']:
            st.write(f"- {book}")
    else:
        st.warning("暂无该类型的详细信息。")

    st.write("---")
    st.write("**维度计分：**")
    st.dataframe(pd.DataFrame([{k: v for k,v in breakdown[axis].items()} for axis in breakdown]))
