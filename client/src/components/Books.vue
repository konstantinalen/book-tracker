<script setup>
import { ref, onMounted } from 'vue'

const books = ref([])

const fetchBooks = async () => {
  try {
    const response = await fetch('http://localhost:3000/api/allbooks')
    const data = await response.json()
    books.value = data
  } catch (error) {
    console.error("Fetch Error:", error)
  }
}

onMounted(() => {
  fetchBooks()
})
</script>

<template>
  <div>
    <table>
      <thead>
        <tr>
          <th>Title</th>
          <th>Author</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="book in books" :key="book.id">
          <td>{{ book.title }}</td>
          <td>{{ book.author }}</td>
        </tr>
        <tr v-if="books.length === 0">
          <td colspan="2">No books yet.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
table {
  margin: 20px auto; 
  width: 80%;
  border-collapse: collapse;
}
th {
  background-color: rgb(192, 191, 191);
  border: 1px solid #cccccc;
  padding: 10px;
}
td {
  text-align: center;
  border: 1px solid #cccccc;
  padding: 8px;
}
td:hover {
  background-color: rgb(214, 212, 212);
}
tbody tr:nth-child(odd) {
  background-color: rgb(245, 243, 243);
}
</style>
