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
<p class="hint">按编号只读查看：色号、升数、净面积与涂布率均为写入时钉选值，不随当前默认色号或遮盖力参数变化。</p>
</div></template>
