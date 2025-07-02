<template>
  <ul class="nav nav-tabs">
    <li class="nav-item">
      <button 
        class="nav-link"
        :class="{ active: currentTab === 'editor' }"
        @click="changeTab('editor')"
      >
        Editor
      </button>
    </li>
    <li class="nav-item">
      <button
        class="nav-link"
        :class="{ active: currentTab === 'preview' }"
        @click="changeTab('preview')"
      >
        Preview
      </button>
    </li>
  </ul>
</template>

<script>
export default {
  props: {
    currentTab: {
      type: String,
      required: true
    }
  },
  methods: {
    changeTab(tab) {
      this.$emit('change-tab', tab);
    }
  }
}
</script>

<style scoped>
</style>