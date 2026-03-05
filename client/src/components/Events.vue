<script setup>
import { ref, onMounted } from 'vue'

const books = ref([])

const fetchBooks = async () => {
  try {
    const response = await fetch('http://localhost:3000/api/scans')
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
          <th>ID</th>
          <th>Title</th>
          <th>Author</th>
          <th>Status</th>
          <th>Last Seen</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="book in books" :key="book.id">
          <td>{{ book.id }}</td>
          <td>{{ book.title }}</td>
          <td>{{ book.author }}</td>
          <td>{{ book.status }}</td>
          <td>{{ new Date(book.last_seen).toLocaleString('el-GR') }}</td>
        </tr>
        <tr v-if="books.length === 0">
          <td colspan="5">No scans yet.</td>
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