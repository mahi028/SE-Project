<template>
  <div v-if="type=='basic'">
    <span class="text-lg font-semibold block mb-1">{{ label }}</span>
    <span v-if="isLink" class="text-primary underline">
      <a :href="href" target="_blank" rel="noopener">{{ value }}</a>
    </span>
    <span v-else>{{ value }}</span>
  </div>
  <div class="flex justify-between m-2" v-else>
    <span class="text-md font-semibold block mb-1">{{ label }}</span>
    <span v-if="isLink" class="text-primary underline">
      <a :href="href" target="_blank" rel="noopener">{{ value }}</a>
    </span>
    <span v-else>{{ value }}</span>
  </div>
</template>

<script setup>
defineProps({
    type: String,
    label: String,
    value: String,
    isLink: Boolean,
    href: String
})
</script>
