<template>

  <div>

    <div class="tabs">
      <ul>
        <li v-for="tab in tabs"
            :class="{ 'is-active': tab.isActive }"
        ><a @click="selectTab(tab)">{{ tab.name }}</a></li>
      </ul>
    </div>

    <div class="tabs-content">

      <slot></slot>

    </div>

  </div>
</template>

<script>

  import tab from './tab.vue';

  export default {

    name: "tabs",

    components: { tab },

    data() {
      return {
        tabs: null
      }
    },

    created () {
      this.tabs = this.$children;
    },

    methods: {
      selectTab (selectedTab) {
        this.tabs.forEach(t => {
          t.isActive = t.name == selectedTab.name;
        })
        selectedTab.isActive = true;
      }
    }

  }
</script>
