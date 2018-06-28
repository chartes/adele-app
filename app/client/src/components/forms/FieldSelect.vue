<template>
    <div class="field">
        <p class="control">
            <label class="label">{{ label }}</label>
            <span class="select" :class="isLoading">
                <select v-model="val" @change="onChange(val)">
                    <option
                            v-if="hasOptions"
                            v-for="opt in options"
                            :key="opt.id"
                            :value="opt.id"
                            :selected="optionSelected"
                            v-html="opt.label"
                    ></option>
                </select>
            </span>
        </p>
    </div>
</template>

<script>
  export default {
    name: "field-select",
    props: {
      options: {
        type: Array
      },
      label: {
        type: String
      },
      selected: {
        type: Number
      },
      onChange: {
        type: Function,
        required: true
      }
    },
    data() {
      return {
        val: this.$props.selected || null
      }
    },
    mounted(){
      this.onChange(this.val);
    },
    methods: {
      optionSelected (optId) {
        return optId === this.selected;
      }
    },
    watch: {
      selected () {
        this.val = this.$props.selected
      }
    },
    computed: {
      hasOptions () {
        return this.options && this.options.length > 0;
      },
      isLoading () {
        return !(this.options && this.options.length > 0) ? 'is-loading': false;
      },
    }
  }
</script>