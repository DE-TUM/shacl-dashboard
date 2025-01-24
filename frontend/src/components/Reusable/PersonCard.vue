<template>
    <div class="card">
      <img :src="photo" alt="Person's photo" class="photo" />
      <h3 class="name">{{ name }}</h3>
      <p class="role">{{ role }}</p>
    </div>
  </template>
  
  <script setup>
  defineProps({
    photo: {
      type: String,
      required: true,
    },
    name: {
      type: String,
      required: true,
    },
    role: {
      type: String,
      required: true,
    },
  });
  </script>
  
  <style scoped>
  .card {
    width: 150px;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
    z-index: inherit !important;
    background-color: #f7f7f7;
  }
/* 
  .card:hover {
  
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
} */
  
  .photo {
    width: 100%;
    height: 100px;
    object-fit: cover;
    border-radius: 4px;
  }
  
  .name {
    margin: 10px 0 5px;
    font-size: 18px;
    font-weight: bold;
  }
  
  .role {
    color: gray;
    font-size: 14px;
  }
  </style>
  