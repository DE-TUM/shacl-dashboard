<template>

        <!-- Search and Filter Component: Takes up the bottom half of the vertical space -->
        <div style="" >
          <Filter v-model:filters="filterState"/>
        </div>
        <!-- Navigation Component: Takes up the top half of the vertical space -->
        <div style="">
          <Search />
        </div>

</template>

<script setup>
import { ref } from 'vue';
import Search from './Reusable/Search.vue'; // Import the Search component
import Filter from './Reusable/Filter.vue'; // Import the Filter component

const inputValue = ref('');
</script>
