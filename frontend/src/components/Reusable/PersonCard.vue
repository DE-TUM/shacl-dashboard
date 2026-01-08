<template>
    <div class="card">
      <img :src="photo" alt="Person's photo" class="photo" />
      <h3 class="name">{{ name }}</h3>
      <p class="role">{{ role }}</p>
    </div>
  </template>
  
  <script setup>
/**
 * PersonCard component
 *
 * Displays information about a person in a card format with photo, name, and role.
 * Used for team member profiles or contributor listings.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <PersonCard
 * //   photo="/path/to/photo.jpg"
 * //   name="Jane Smith"
 * //   role="Developer"
 * // />
 *
 * @prop {String} photo - Path to the person's photo
 * @prop {String} name - The person's name
 * @prop {String} role - The person's role or title
 *
 * @dependencies
 * - vue (Composition API)
 *
 * @style
 * - Card-style container with border, shadow, and rounded corners
 * - Photo displayed with consistent sizing and cropping
 * - Clear typography for name and role with differentiated styling
 * 
 * @returns {HTMLElement} A card displaying a person's information with their photo at the top,
 * name displayed prominently below the photo, and role/title shown in smaller text at the bottom.
 */
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
