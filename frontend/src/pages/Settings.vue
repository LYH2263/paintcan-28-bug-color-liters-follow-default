<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const s = ref({})
const code = ref('')
const saved = ref('')
const err = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  code.value = s.value.default_color_batch || ''
})
const save = async () => {
  err.value = ''; saved.value = ''
  try {
    const r = await postJSON('/api/settings/default-color-batch', { default_color_batch: code.value })
    saved.value = r.default_color_batch
    s.value = { ...s.value, default_color_batch: r.default_color_batch }
  } catch (e) { err.value = e.message }
}
</script>
<template><div class="page"><h1>设置</h1>
<label>默认色号 <input v-model="code" /></label>
<button @click="save">保存默认色号</button>
<p v-if="err" class="err">{{ err }}</p>
<p v-if="saved">已保存：{{ saved }}（仅影响此后新房测算，历史记录不变）</p>
<table style="margin-top:1rem"><tr v-for="(v,k) in s" :key="k"><td>{{ k }}</td><td>{{ v }}</td></tr></table>
</div></template>
