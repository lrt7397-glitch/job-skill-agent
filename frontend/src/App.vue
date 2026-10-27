<template>
  <div class="app-root">
    <!-- 顶部栏 -->
    <header class="app-header">
      <div class="header-title">BOSS 职位技能生成器</div>
      <el-button type="primary" :loading="loadingJobs" @click="loadJobs">
        <el-icon><Refresh /></el-icon>
        <span style="margin-left: 4px">刷新数据</span>
      </el-button>
    </header>

    <!-- 主体：左 60% / 右 40% -->
    <div class="app-body">
      <!-- 左栏 -->
      <section class="left-pane">
        <JobFilter
          v-model:salary="salaryFilter"
          v-model:degree="degreeFilter"
          :total="jobs.length"
          :filtered="filteredJobs.length"
        />
        <div class="left-scroll">
          <JobList :jobs="filteredJobs" @select-job="onSelectJob" />
        </div>
      </section>

      <!-- 右栏 -->
      <section class="right-pane">
        <AgentChat :selected-job="selectedJob" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { fetchJobs } from './api'
import JobFilter from './components/JobFilter.vue'
import JobList from './components/JobList.vue'
import AgentChat from './components/AgentChat.vue'

const jobs = ref([])
const loadingJobs = ref(false)
const salaryFilter = ref('all')
const degreeFilter = ref('all')
const selectedJob = ref(null)

// 前端筛选：工资从 salary 字符串解析下限，学历匹配 degree 字段
const filteredJobs = computed(() => {
  return jobs.value.filter(job => {
    if (salaryFilter.value !== 'all') {
      const match = (job.salary || '').match(/(\d+)-(\d+)K/)
      if (!match) return false
      const low = parseInt(match[1])
      if (salaryFilter.value === '10-20' && !(low >= 10 && low < 20)) return false
      if (salaryFilter.value === '20-50' && !(low >= 20 && low < 50)) return false
      if (salaryFilter.value === '50+' && low < 50) return false
    }
    if (degreeFilter.value !== 'all' && job.degree !== degreeFilter.value) return false
    return true
  })
})

async function loadJobs() {
  loadingJobs.value = true
  try {
    const data = await fetchJobs()
    jobs.value = data.jobs || []
    if (data.message) {
      ElMessage.success(data.message)
    }
  } catch (e) {
    ElMessage.error(e.message || '获取职位列表失败')
    jobs.value = []
  } finally {
    loadingJobs.value = false
  }
}

function onSelectJob(job) {
  // 每次点击都生成新引用并附带时间戳，确保 watch 能重复触发同一职位
  selectedJob.value = { ...job, _t: Date.now() }
}

onMounted(loadJobs)
</script>

<style scoped>
.app-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  z-index: 10;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #00c2b3;
}

.app-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

.left-pane {
  width: 60%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #ebeef5;
  background: #f5f7fa;
}

.left-scroll {
  flex: 1;
  overflow-y: auto;
}

.right-pane {
  width: 40%;
  display: flex;
  flex-direction: column;
  background: #fff;
}
</style>