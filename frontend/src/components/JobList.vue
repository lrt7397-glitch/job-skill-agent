<template>
  <div class="job-list">
    <div v-if="jobs.length === 0" class="empty-tip">
      暂无职位数据，请先运行 python main.py 生成数据，或点击右上角"刷新数据"
    </div>
    <div
      v-for="job in jobs"
      :key="job.job_id || (job.title + job.company)"
      class="job-card"
    >
      <div class="card-header">
        <span class="job-title">{{ job.title }}</span>
        <span class="job-salary">{{ job.salary }}</span>
      </div>
      <div class="card-company">{{ job.company }}</div>
      <div class="card-meta">
        <span v-if="job.city">{{ job.city }}</span>
        <span v-if="job.area">·{{ job.area }}</span>
        <span v-if="job.experience">·{{ job.experience }}</span>
        <span v-if="job.degree">·{{ job.degree }}</span>
      </div>
      <div class="card-skills">
        <span v-for="skill in job.skills" :key="skill" class="skill-tag">{{ skill }}</span>
      </div>
      <div class="card-footer">
        <el-button size="small" type="primary" plain @click="$emit('select-job', job)">
          生成技能
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  jobs: { type: Array, default: () => [] }
})
defineEmits(['select-job'])
</script>

<style scoped>
.job-list {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-tip {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 40px 0;
}

.job-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  padding: 14px 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.job-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.job-salary {
  font-size: 14px;
  color: #00c2b3;
  font-weight: 600;
}

.card-company {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-meta {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.card-skills {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.skill-tag {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 2px 10px;
  font-size: 12px;
  color: #606266;
}

.card-footer {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}
</style>