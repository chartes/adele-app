<template>
    <div class="field">
        <p class="control">
            <label class="label">{{ label }}</label>
            <span class="select">
                <select @change="onChange($event)">
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
    data() {
      console.log("select", this.$props)
      return {
        val: this.$props.selected || this.$props.options[0].id
      }
    },
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
    }
  }
</script>