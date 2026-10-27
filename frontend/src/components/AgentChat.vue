<template>
  <div class="agent-chat">
    <div class="chat-header">技能生成对话</div>

    <!-- 消息列表 -->
    <div class="chat-messages" ref="msgBox">
      <div v-if="messages.length === 0" class="chat-empty">
        从左栏选择职位卡片，或直接在下方输入"职位名 技能1 技能2"后发送
      </div>
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="msg-row"
        :class="msg.role === 'user' ? 'msg-right' : 'msg-left'"
      >
        <div class="bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-agent'">
          {{ msg.content }}
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="chat-input">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        resize="none"
        placeholder="输入职位名与技能，如：Java后端 Python Java MySQL（Ctrl+Enter 发送）"
        @keydown.enter.ctrl="send"
      />
      <el-button
        type="primary"
        :loading="loading"
        :disabled="loading || !inputText.trim()"
        @click="send"
        style="margin-top: 8px; width: 100%"
      >
        {{ loading ? '生成中...' : '发送' }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { generateSkills } from '../api'

const props = defineProps({
  selectedJob: { type: Object, default: null }
})

const messages = ref([])
const inputText = ref('')
const loading = ref(false)
const msgBox = ref(null)

// 接收到父组件选中的职位：自动把 title + skills 填入输入框并自动发送
watch(
  () => props.selectedJob,
  (job) => {
    if (!job) return
    const title = job.title || ''
    const skills = (job.skills || []).join(' ')
    inputText.value = `${title} ${skills}`.trim()
    send()
  }
)

function scrollToBottom() {
  nextTick(() => {
    if (msgBox.value) {
      msgBox.value.scrollTop = msgBox.value.scrollHeight
    }
  })
}

async function send() {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  // 解析：第一段为职位名，其余为技能标签
  const parts = text.split(/\s+/)
  const jobTitle = parts[0] || ''
  const skills = parts.slice(1)

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  scrollToBottom()

  if (!skills.length) {
    messages.value.push({
      role: 'agent',
      content: '请同时输入职位名和技能标签，用空格分隔，例如：Python后端 Python Django MySQL'
    })
    scrollToBottom()
    return
  }

  loading.value = true
  try {
    const data = await generateSkills(jobTitle, skills)
    messages.value.push({ role: 'agent', content: data.skills_text || '（未生成内容）' })
  } catch (e) {
    ElMessage.error(e.message || '生成失败')
    messages.value.push({ role: 'agent', content: `生成失败：${e.message || '未知错误'}` })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
.agent-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  height: 48px;
  line-height: 48px;
  padding: 0 16px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}

.chat-empty {
  text-align: center;
  color: #909399;
  font-size: 13px;
  margin-top: 40px;
}

.msg-row {
  display: flex;
  margin-bottom: 12px;
}

.msg-left {
  justify-content: flex-start;
}

.msg-right {
  justify-content: flex-end;
}

.bubble {
  max-width: 80%;
  padding: 10px 14px;
  font-size: 13px;
  line-height: 1.6;
  border-radius: 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble-user {
  background: #d6eaf9;
  color: #1d2129;
}

.bubble-agent {
  background: #fff;
  border: 1px solid #e4e7ed;
  color: #303133;
}

.chat-input {
  padding: 12px 16px;
  border-top: 1px solid #ebeef5;
  background: #fff;
  flex-shrink: 0;
}
</style>