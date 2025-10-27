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
    "ESTJ": {"title": "架构解密者", "description": "你痴迷于“情节逻辑闭环”，喜欢扎根现实、无漏洞的故事——既要有紧凑的外部事件，又要符合现实规则，最终结局必须是情节与人物动机的必然结果。", "kind":["侦探/推理小说和逻辑缜密的历史悬疑小说"],"books": ["《清明上河图密码》", "《东方快车谋杀案》", "《坏小孩》"]},

    "ENTJ": {"title": "世界规则掌控者", "description": "你享受“虚构世界里的严谨逻辑”——偏爱有完整设定的故事，情节要紧凑，且所有事件都要符合这个世界的“自定规则”，结局必须清晰交代冲突解决方式","kind":["硬科幻小说、规则严谨的史诗奇幻、高概念设定推理"], "books": ["《三体》", "《基地》", "《沙丘》"]},

    "ISTJ": {"title": "人性逻辑观察者", "description": "你关注“现实人物的心理逻辑”——不追求强情节，更爱通过日常细挖掘人物内心，且人物的心理转变必须符合现实逻辑，结局要明确交代人物的最终选择", "kind":["现实向心理小说、家庭伦理小说、细腻派社会写实作品"],"books": ["《活着》", "《包法利夫人》", "《人世间》"]},

    "INTJ": {"title": "隐喻逻辑解读师", "description": "你喜欢“用虚构外壳剖析心理逻辑”——故事可以有奇幻/科幻元素，但核心是挖掘人物内心，且人物心理变化要符合“隐喻逻辑”，结局需明确人物的自我和解/认知。", "kind":["隐喻型科幻/奇幻、心理向寓言小说、设定服务于人物的作品"],"books": ["《克拉拉与太阳》", "《失明症漫记》", "《蝇王》"]},

    "ESTP": {"title": "现实谜题探索者", "description": "你享受“现实情节的逻辑留白”——喜欢基于现实的悬疑/探案故事，情节要紧凑且符合现实逻辑，可让结局留下“思想层面的开放”，重点是通过逻辑推理过程引发对现实的思考","kind":["社会派推理小说、现实向悬疑小说、逻辑严谨的“问题小说”"], "books": ["《白夜行》", "《局外人》", "《长夜难明》"]},

    "ENTP": {"title": "设定谜题思辨者", "description": "你偏爱“虚构设定的逻辑延伸”——喜欢有创新设定的故事，情节要围绕设定展开，结局可以不“解决所有问题”，但必须在现有逻辑内自洽，重点是引发对设定背后思想的讨论。", "kind":["思辨型硬科幻、设定开放的奇幻推理、高概念思想小说"],"books": ["《你一生的故事》", "《环形使者》", "《黑暗的左手》"]},

    "ISTP": {"title": "人性思考者", "description": "你关注“现实人物的心理留白”——喜欢通过日常细节刻画人物内心，人物心理变化符合现实逻辑，但不介意结局留下“人物未来的开放”，重点是通过心理逻辑引发对人性的思考", "kind":["现实向心理散文小说、细腻派成长小说、人物导向的“切片式”作品"],"books": ["《挪威的森林》", "《斯通纳》", "《山茶文具店》"]},

    "INTP": {"title": "隐喻心理思辩者", "description": "你喜欢“虚构隐喻的心理留白”——故事可以有奇幻/科幻元素，核心是挖掘人物内心，且心理变化符合隐喻逻辑，结局可以不“完成自我和解”，重点是通过隐喻引发对内心世界的思辨。", "kind":["隐喻型心理奇幻、思辨向科幻小说、设定服务于心理的作品"],"books": ["《海浪》", "《树上的男爵》", "《佩德罗·巴拉莫》"]},

    "ESFJ": {"title": "现实情感追随者", "description": "你沉迷于“现实情节中的情感闭环”——喜欢有紧凑外部事件的现实故事，重点是事件引发的人物情感变化，结局必须让情感得到明确安放。","kind":["现实向情感小说、家庭史诗、温暖系冒险小说"], "books": ["《平凡的世界》", "《山茶文具店》", "《夺宝奇兵》"]},

    "ENFJ": {"title": "奇幻情感守护者", "description": "你享受“虚构情节中的情感圆满”——偏爱有奇幻/科幻设定的紧凑故事，核心是人物在虚构事件中的情感联结，结局必须让情感得到明确圆满，服务于情感表达。", "kind":["情感向奇幻小说、温暖系科幻、冒险向童话改编"],"books": ["《霍比特人》", "《少年Pi的奇幻漂流》", "《星尘》"]},

    "ISFJ": {"title": "人间温情记录者", "description": "你沉醉于“现实日常里的情感沉淀”——不追求强情节，更爱通过平凡生活细节捕捉人物细腻情感，人物情感变化真实可感，看重“生活本身的情感圆满”。","kind":["日常向温情小说、家庭琐事纪实小说、细腻派邻里/职场情感作品"], "books": ["《佐贺的超级阿嬷》", "《深夜食堂》", "《我们仨》"]},

    "INFJ": {"title": "奇幻心灵治愈者", "description": "你偏爱“虚构设定下的情感和解”——故事可以有奇幻/科幻元素，但核心是挖掘人物内心的情感困境，虚构设定为情感表达服务，看重“心灵层面的圆满”。", "kind":["治愈系奇幻小说、情感向寓言故事、设定服务于心理治愈的作品"],"books": ["《小王子》", "《海洋之歌》", "《你在天堂里遇见的五个人》"]},

    "ESFP": {"title": "现实情感漫游者", "description": "你享受“现实情节中的情感切片”——喜欢有鲜活外部事件的现实故事，重点是事件中迸发的即时情感，情节紧凑但不追求“最终圆满”，看重“情感体验的真实感", "kind":["公路小说、都市情感切片小说、现实向冒险短篇集"],"books": ["《漫长的告别》", "《奥吉·马奇历险记》", "《飞行家》"]},

    "ENFP": {"title": "奇幻情感探索者", "description": "你痴迷于“虚构情节中的情感可能”——偏爱有奇幻/科幻设的灵动故事，核心是人物在虚构事件中遇到的多元情感，情节轻快，结局可以留下情感延伸，看重“情感探索的新鲜感”。", "kind":["轻奇幻冒险小说、脑洞向情感故事、设定灵动的短篇集"],"books": ["《银河系漫游指南》", "《爱丽丝梦游仙境》", "《夜晚的潜水艇》"]},

    "ISFP": {"title": "生活情绪捕捉者", "description": "你关注“现实日常里的情感余韵”——不喜欢强情节，更爱通过细微场景捕捉人物的隐秘情绪，结局留下情感余韵，看重“情绪体验的细腻感”。","kind":["散文化现实小说、情绪向短篇集、日常感私小说"], "books": ["《古都》", "《情人》", "《秋园》"]},

    "INFP": {"title": "幻梦情感沉思者", "description": "你沉醉于“虚构意象里的情感哲思”——故事多有诗意的奇幻/象征元素，核心是人物在虚构意象中探索深层情感，情感表达偏向“哲理性”，留下对情感本质的沉思，看重“情感与思想的联结”。", "kind":["诗意奇幻小说、象征主义情感作品、哲思向寓言故事"],"books": ["《海浪》", "《阿莱夫》", "《佩德罗·巴拉莫》"]},
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
    cnt = 0
    PLACEHOLDER = "—— 请选择 ——"
    for idx, q in enumerate(QUESTIONS, start=1):
        cnt = idx
        st.write(f"**{cnt}.{q['text']}**")

        # 使用占位选项使得打开页面时看起来像 "未选择"
        labels = [PLACEHOLDER] + [opt[0] for opt in q['options']]
        choice = st.selectbox("", labels, key=q['id'])

        # 将选项文本映射为轴上的值（如 'E' / 'I'）
        label_to_val = {opt[0]: opt[1] for opt in q['options']}
        if choice == PLACEHOLDER:
            chosen_value = None
        else:
            chosen_value = label_to_val.get(choice)

        answers[q['id']] = chosen_value
        st.divider()
    submitted = st.form_submit_button("提交并查看结果")

if submitted:
    # 校验是否有未填题目
    unanswered = [i+1 for i, q in enumerate(QUESTIONS) if answers.get(q['id']) is None]
    if unanswered:
        st.error("以下题目未填写，请完成后再提交：" + '，'.join([f"第{n}题" for n in unanswered]))
    else:
        mbti, breakdown = compute_mbti(answers)
        st.success(f"你的文学 MBTI 类型是：**{mbti}**")
        profile = MBTI_PROFILES.get(mbti)
        if profile:
            st.header(profile['title'])
            st.write(profile['description'])
            st.write("**偏好类型：** " + '，'.join(profile['kind']))
            st.write("**推荐书目：**")
            for book in profile['books']:
                st.write(f"- {book}")
        else:
            st.warning("暂无该类型的详细信息。")

        # 改进版：更清晰的维度计分显示
        # ------------------------------------
        st.write("---")
        st.subheader("维度计分结果")

        axis_labels = {
            "EI": "焦点取向（E: 情节驱动 / I: 内心世界）",
            "SN": "风格取向（S: 现实主义 / N: 想象主义）",
            "TF": "决策取向（T: 逻辑架构 / F: 情感共鸣）",
            "JP": "态度取向（J: 闭合结局 / P: 开放诠释）"
        }

        for axis, scores in breakdown.items():
            left_key, right_key = list(scores.keys())
            left_score = scores[left_key]
            right_score = scores[right_key]

            # 高亮当前倾向
            if left_score > right_score:
                tendency = left_key
                tendency_label = f"**{left_key} 型倾向更明显**"
            elif right_score > left_score:
                tendency = right_key
                tendency_label = f"**{right_key} 型倾向更明显**"
            else:
                tendency = "平衡"
                tendency_label = "两者倾向接近"

            # 视觉显示
            st.markdown(f"#### {axis_labels[axis]}")
            progress = left_score / (left_score + right_score)
            st.progress(progress)
            st.write(f"{left_key}: {left_score}  vs  {right_key}:   {right_score} —— {tendency_label}")
            st.markdown("---")

