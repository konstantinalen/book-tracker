<script setup>
</script>

<template>
  <table>
    
    <thead>
      <tr>
        <th>Title</th>
      </tr>
    </thead>
    
    <tbody>
     
    </tbody>
    
  </table>
</template>

<style scoped>
  table
  {
    margin: 0 auto; 
    width: 50%;
    border-collapse: collapse;
  }

  th
  {
    background-color: rgb(192, 191, 191);
    border: 1px solid #cccccc;
  }

  td 
  {
    text-align: center;
    border: 1px solid #cccccc;
  }

  td:hover
  {
    background-color: rgb(214, 212, 212);
  }

  tbody tr:nth-child(odd) 
  {
    background-color: rgb(245, 243, 243);
  }
</style>
