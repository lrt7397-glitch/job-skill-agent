<template>
  <div class="job-filter">
    <div class="filter-row">
      <span class="filter-label">工资：</span>
      <el-select v-model="salaryModel" size="small" style="width: 120px">
        <el-option label="全部" value="all" />
        <el-option label="10-20K" value="10-20" />
        <el-option label="20-50K" value="20-50" />
        <el-option label="50K以上" value="50+" />
      </el-select>

      <span class="filter-label" style="margin-left: 16px">学历：</span>
      <el-select v-model="degreeModel" size="small" style="width: 100px">
        <el-option label="全部" value="all" />
        <el-option label="大专" value="大专" />
        <el-option label="本科" value="本科" />
        <el-option label="硕士" value="硕士" />
        <el-option label="博士" value="博士" />
      </el-select>

      <span class="filter-count">
        共 {{ total }} 条 / 筛选后 {{ filtered }} 条
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  salary: { type: String, default: 'all' },
  degree: { type: String, default: 'all' },
  total: { type: Number, default: 0 },
  filtered: { type: Number, default: 0 }
})

const emit = defineEmits(['update:salary', 'update:degree'])

// v-model 双向绑定：通过 computed get/set 转发 update 事件
const salaryModel = computed({
  get: () => props.salary,
  set: v => emit('update:salary', v)
})
const degreeModel = computed({
  get: () => props.degree,
  set: v => emit('update:degree', v)
})
</script>

<style scoped>
.job-filter {
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.filter-row {
  display: flex;
  align-items: center;
}

.filter-label {
  font-size: 13px;
  color: #606266;
}

.filter-count {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}
</style>