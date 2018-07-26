<template>
    <article class="message" :class="type">
        <div class="message-body">
            <p v-html="body"></p>
        </div>
    </article>
</template>

<script>
  export default {
    name: "minimal-message",
    props: ['type', 'body']
  }
</script>