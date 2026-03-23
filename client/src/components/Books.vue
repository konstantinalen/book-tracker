<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

const books = ref([])
let socket;

const fetchBooks = async () => {
  try {
    const response = await fetch('http://localhost:3000/api/books')
    books.value = await response.json()
  } catch (error) {
    console.error('Error fetching books:', error)
  }
}

onMounted(() => {
  fetchBooks() // Initial load
  
  // Connect to the Socket server and listen for updates
  socket = io('http://localhost:3000')
  socket.on('new_scan_event', () => {
    console.log("Live update received! Refreshing table...")
    fetchBooks()
  })
})

onUnmounted(() => {
  if (socket) socket.disconnect()
})
</script>

<template>
  <div>
    <h2>Library Inventory</h2>
    <table>
      <thead>
        <tr>
          <th>EPC (Tag ID)</th>
          <th>Title</th>
          <th>Author</th>
          <th>Status</th>
          <th>Last Seen</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="book in books" :key="book.id">
          <td>{{ book.epc }}</td>
          <td>{{ book.title }}</td>
          <td>{{ book.author || '—' }}</td>
          <td>
            <span :class="{'status-in': book.status === 'IN', 'status-out': book.status === 'OUT'}">
              {{ book.status }}
            </span>
          </td>
          <td>{{ new Date(book.last_seen).toLocaleString() }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
  h2 {
    text-align: center;
    margin-bottom: 20px;
  }

  table {
    margin: 0 auto; 
    width: 80%;
    border-collapse: collapse;
    background-color: white;
    color: black;
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

  .status-in {
    color: green;
    font-weight: bold;
  }
  
  .status-out {
    color: red;
    font-weight: bold;
  }
</style>
