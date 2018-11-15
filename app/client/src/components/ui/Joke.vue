<template>
  <transition name="fade">
    <div id="joke">
      <img id="astronaut" src="/adele/static/images/astronaut.svg"/>
    </div>
  </transition>
</template>

<script>
  export default {
    name: 'Joke'
  }
</script>

<style scoped>
  #joke {
    background: #000 url(/adele/static/images/solar-system.svg) no-repeat 50% 50%;
    background-size: cover;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
  }
  #astronaut {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    animation: astronaut-rotation 5s infinite linear;
  }
  @keyframes astronaut-rotation {
    0% {
      transform: translate(-50%, -50%) rotate(-30deg);
    }
    100% {
      transform: translate(-50%, -50%) rotate(330deg);
    }
  }
</style>