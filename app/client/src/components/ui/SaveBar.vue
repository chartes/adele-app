<template>
    <transition name="slideup">
        <div class="save-bar" v-show="visible">
            <div class="container save-bar__container">

                <save-bar-button :action="action" :status="buttonStatus" />

            </div>
        </div>
    </transition>
</template>

<script>

  import { mapState } from 'vuex';
  import SaveBarButton from "./SaveBarButton";
  export default {
    name: "save-bar",
    components: {SaveBarButton},
    props: {
      disabled: {
        type: Boolean,
        default: true
      },
      action: {
        type: Function,
        required: true
      }
    },
    data () {
      return {
        visible: false,
        visibilityTimeout: null,
        statusTimeout: null,
        buttonStatus: 'normal'
      }
    },
    beforeDestroy () {
      clearTimeout(this.visibilityTimeout)
      clearTimeout(this.statusTimeout)
    },
    methods: {
      changeVisibilityWithDelay (isVisible) {
        this.visibilityTimeout = setTimeout(() => {
          this.visible = isVisible;
        }, 2000)
      },
      changeStatusWithDelay (status) {
        this.statusTimeout = setTimeout(() => {
          this.buttonStatus = status;
        }, 3000)
      }
    },
    watch: {
      savingStatus () {
        switch (this.savingStatus) {
          case 'tobesaved':
            this.visible = true;
            this.buttonStatus = 'normal';
            break;
          case 'uptodate':
            this.buttonStatus = 'success';
            this.changeVisibilityWithDelay(false);
            this.changeStatusWithDelay('normal')
            break;
          case 'error':
            this.visible = true;
            this.buttonStatus = 'error';
            this.changeStatusWithDelay('normal')
            break;
          case 'saving':
            this.visible = true;
            this.buttonStatus = 'working';
            break;
        }
      }
    },
    computed: {
      ...mapState('transcription', ['savingStatus'])
    }
  }
</script>

<style scoped>
</style>