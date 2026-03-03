<script setup>

</script>

<template>
  <nav>
    <div class="bar">
      <router-link to="/events" class="tabs">Track Books</router-link>
      <router-link to="/books" class="tabs">All Books</router-link>
    </div>
  </nav>

  <main class="content">
    <router-view></router-view>
  </main>
</template>

<style scoped>
  nav
  {
    background-color: rgb(186, 189, 189);
  }

  .bar 
  {
    display: flex;
    width: 100%;
  }

  .tabs 
  {
    margin-left: 29%;
    cursor: pointer;
    font-weight: bold;
    font-size: larger;
    padding: 15px;
    text-decoration: none; 
    color: #333; 
  }

  .tabs:hover 
  {
    color: rgb(80, 80, 80);
  }

  .router-link-active 
  {
    color: black;
    border-bottom: 3px solid rgb(35, 35, 36);
  }

  .content 
  {
    padding: 20px;
  }
</style>
