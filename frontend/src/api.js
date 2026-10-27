// 统一封装后端接口调用，全部走相对路径 /api，靠 Vite proxy 转发
// 错误统一抛出 Error，由调用方用 ElMessage.error 展示中文提示

/**
 * 获取职位列表
 * @returns {Promise<{jobs: Array, message: string}>}
 */
export async function fetchJobs() {
  const resp = await fetch('/api/jobs')
  const data = await resp.json()
  if (!resp.ok) {
    throw new Error(data.detail || data.error || '获取职位列表失败')
  }
  return data
}

/**
 * 生成技能描述
 * @param {string} jobTitle
 * @param {string[]} skills
 * @returns {Promise<{skills_text: string}>}
 */
export async function generateSkills(jobTitle, skills) {
  const resp = await fetch('/api/agent/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_title: jobTitle, skills })
  })
  const data = await resp.json()
  if (!resp.ok) {
    throw new Error(data.detail || data.error || '生成技能描述失败')
  }
  return data
}

/**
 * 触发爬虫
 * @param {object} params { query, city, salary, degree }
 * @returns {Promise<{message: string}>}
 */
export async function triggerScrape(params = {}) {
  const resp = await fetch('/api/scrape', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  })
  const data = await resp.json()
  if (!resp.ok) {
    throw new Error(data.detail || data.error || '触发爬虫失败')
  }
  return data
}