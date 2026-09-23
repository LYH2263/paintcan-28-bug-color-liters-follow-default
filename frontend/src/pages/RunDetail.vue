<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON } from '../api'
const route = useRoute()
const r = ref(null)
const load = async () => { r.value = await getJSON(`/api/history/${route.params.id}`) }
onMounted(load); watch(() => route.params.id, load)
</script>
<template><div class="page" v-if="r"><h1>测算记录 #{{ r.id }}</h1>
<p>色号 <b>{{ r.color_batch || '—' }}</b></p>
<p>升数 <span class="hero-num">{{ r.liters ?? r.result?.liters ?? '—' }} L</span></p>
<p>净面积 {{ r.net_m2 ?? r.result?.net_m2 ?? '—' }} m² · 涂布率 {{ r.coverage ?? r.result?.coverage ?? '—' }} m²/L · {{ r.coats ?? r.result?.coats ?? '—' }} 遍</p>
<p>房间 {{ r.room_id ?? '—' }} · {{ r.created_at }}</p>
<p class="hint">详情升数随当前默认涂布率刷新；列表仍显示写入时钉选值。</p>
</div></template>
