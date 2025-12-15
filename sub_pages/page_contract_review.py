# contract_review_app.py
# 运行前请先安装必要的库:
# pip install streamlit openai python-docx

import openai
import streamlit as st
from docx import Document
import fitz
from prompt_template.contract_review_template import review_key_points, contract_template

from app_config.keys_config import AZURE_OPENAI_TOKEN, AZURE_OPENAI_ENDPOINT

AI_MODEL = "o3-mini"  # 可以根据需要选择不同的模型

# --- 配置 OpenAI/Azure OpenAI ---
# 建议使用 Streamlit secrets 来管理你的 API 密钥
# 例如: st.secrets["OPENAI_API_KEY"]
# 这里为了演示，我们假设密钥已设置在环境变量或 secrets 中
try:
    # 替换为你自己的 OpenAI 或 Azure OpenAI 客户端初始化方式
    # openai.api_key = st.secrets["OPENAI_API_KEY"]
    # 如果使用 Azure, 初始化方式如下:
    client = openai.AzureOpenAI(
        api_key=AZURE_OPENAI_TOKEN,
        api_version="2024-12-01-preview",
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )
except Exception as e:
    st.error("OpenAI API 密钥未配置，请在 Streamlit secrets 中设置。")
    st.stop()


def read_docx_text(file_like_object):
    """从上传的 .docx 文件对象中读取文本"""
    try:
        doc = Document(file_like_object)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"读取 Word 文档时出错: {e}")
        return None


def read_pdf_to_single_string(pdf_file_bytes: bytes) -> str:

    full_text = ""
    try:
        with fitz.open(stream=pdf_file_bytes, filetype="pdf") as doc:
            # 遍历每一页
            for page in doc:
                # 提取当前页的文本并追加到总字符串
                full_text += page.get_text()
    except Exception as e:
        print(f"处理上传文件时发生错误: {e}")
        return ""

    return full_text


def get_contract_review(contract_text, review_points):
    """构建 Prompt 并调用大模型获取审核结果"""

    # 1. 构建动态的任务指令
    tasks = ""
    if "合同要点识别" in review_points:
        str_review_key_points = "\n".join(review_key_points)
        tasks += "- **合同要点识别**: " + str_review_key_points + "\n"
    if "风险识别" in review_points:
        tasks += "- **风险识别**: 识别并列出合同中对甲方（我方）可能存在的不利条款、模糊表述、缺失的关键要素或潜在的法律风险。\n"
    if "核心条款摘要" in review_points:
        tasks += "- **核心条款摘要**: 简洁地总结合同的核心商业条款，例如：合同目的、合同期限、付款条件、交付物、违约责任、知识产权归属等。\n"
    if "要素完整性检查" in review_points:
        tasks += "- **要素完整性检查**: 检查合同是否包含了通用合同应具备的基本要素，如双方主体信息、标的、数量、质量、价款、履行期限、地点和方式、违约责任、解决争议的方法等。\n"
    if "提出修改建议" in review_points:
        tasks += "- **提出修改建议**: 针对识别出的风险点或模糊条款，提出具体的、可操作的修改建议。\n"

    if not tasks:
        return "错误：请至少选择一个审核要点。"

    # 2. 构建完整的 Prompt
    system_prompt = "你是一位经验丰富的法律事务助理，你的任务是帮助用户快速审阅合同文本，识别潜在问题并提供摘要。请以专业、严谨、中立的口吻进行分析。"

    user_prompt = f"""
请根据以下合同文本，完成下列审核任务：
{tasks}

请严格按照任务要求，以清晰的 Markdown 格式输出你的审核报告，每个审核任务使用二级标题（##）分隔。

【合同模板】
---
{contract_template}
---

【合同原文】
---
{contract_text}
---

请在报告的最后，附上以下免责声明：
**免责声明**: 本报告由AI生成，仅供初步参考，不能替代专业法律顾问的正式意见。
"""

    # print(f"构建的用户提示:\n{user_prompt}")
    # print("###########################################")
    # print(f"使用的系统提示:\n{system_prompt}")

    try:
        with st.spinner("AI 正在深度分析合同，请稍候..."):
            # 3. 调用大模型 API
            response = client.chat.completions.create(
                model=AI_MODEL,  # 建议使用能力更强的模型，如 gpt-4, gpt-4o 等
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                # temperature=0.2, # 较低的 temperature 使输出更稳定、严谨
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"调用 AI 模型时出错: {e}"


# --- Streamlit 应用界面 ---
st.title(":material/description: AI 合同智能初审助手")
st.markdown(
    "上传您的合同文件（.docx / pdf），选择需要审核的要点，AI 将为您提供一份初步的审核报告。注意：docx 请使用Microsoft Office 官方文件，其他软件导出的兼容格式可能会导致翻译错误。审核只针对合同文本内容，不包括图片"
)

# 1. 文件上传
uploaded_file = st.file_uploader(
    "上传合同文件", type=["docx", "pdf"], help="请上传 .docx .pdf 格式的合同文件。"
)

# 2. 选择审核要点
# review_options = ["合同要点识别", "风险识别", "核心条款摘要", "要素完整性检查", "提出修改建议"]
review_options = ["合同要点识别", "提出修改建议"]
selected_points = st.multiselect(
    "选择您关注的审核要点 (可多选)",
    options=review_options,
    default=review_options[:1],  # 默认选中前两项
)

# 3. 开始审核按钮
if st.button("🚀 开始审核"):
    if uploaded_file is not None and selected_points:
        file_name = uploaded_file.name

        if file_name.lower().endswith(".pdf"):
            # 读取 PDF 文件内容
            contract_text = read_pdf_to_single_string(uploaded_file.read())
        elif file_name.lower().endswith(".docx"):
            # 读取文件内容
            contract_text = read_docx_text(uploaded_file)

        if contract_text:
            # 获取审核报告
            review_result = get_contract_review(contract_text, selected_points)

            # 展示结果
            st.subheader("AI 审核报告")
            st.markdown(review_result)

    elif uploaded_file is None:
        st.warning("请先上传一个合同文件。")
    else:
        st.warning("请至少选择一个审核要点。")
