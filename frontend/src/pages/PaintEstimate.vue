<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const room_id = ref(1)
const color_batch = ref('')
const defaults = ref({})
const history = ref([])
const out = ref(null)
const err = ref('')
onMounted(async () => {
  defaults.value = await getJSON('/api/settings')
  history.value = (await getJSON('/api/history')).items
})
const usedBatches = computed(() =>
  [...new Set(history.value.map(h => h.color_batch).filter(Boolean))])
const run = async (persist) => {
  err.value = ''
  out.value = null
  const body = { room_id: room_id.value, persist }
  if (color_batch.value.trim()) body.color_batch = color_batch.value.trim()
  try {
    out.value = await postJSON('/api/estimate', body)
    history.value = (await getJSON('/api/history')).items
  } catch (e) { err.value = e.message }
}
</script>
<template><div class="page"><h1>估漆工作台</h1>
<label>房间ID <input v-model.number="room_id" /></label>
<label>色号批次
  <input v-model="color_batch" list="used-batches"
    :placeholder="`留空用默认：${defaults.default_color_batch || '（未设置）'}`" />
</label>
<datalist id="used-batches">
  <option v-for="b in usedBatches" :key="b" :value="b"></option>
</datalist>
<button @click="run(false)">试算(不落库)</button>
<button @click="run(true)">估算并记录</button>
<p v-if="err" class="err">{{ err }}</p>
<p v-if="out">色号 <b>{{ out.color_batch }}</b> · 净 {{ out.net_m2 }} m² ·
  <span class="hero-num">{{ out.liters }} 升</span> · {{ out.coats }} 遍
  <span v-if="!out.run_id">（试算，未写记录）</span></p></div></template>
