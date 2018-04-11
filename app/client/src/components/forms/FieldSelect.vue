<template>
    <div class="field">
        <p class="control">
            <label class="label">{{ label }}</label>
            <span class="select">
                <select v-model="val" @change="onChange(val)">
                    <option disabled value="">Choisissez</option>
                    <option
                            v-for="opt in options"
                            :key="opt.id"
                            :value="opt.id"
                            :selected="opt.id == selected"
                    >{{ opt.label }}</option>
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
      console.log("select", this.$props)
      return {
        val: this.$props.selected || this.$props.options[0].id
      }
    },
    mounted(){
      this.$props.onChange(this.val);
    },
    methods: {
      onSelChange() {
        console.log("select change", this.val)
      }
    }
  }
</script>