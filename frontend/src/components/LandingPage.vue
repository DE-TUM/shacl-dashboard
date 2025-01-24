<template>
    <div class="landing-page">
      <!-- Main Card for SHACL Dashboard and Input Form -->
      <div class="card">
        <!-- Left side of the card (gradient background) -->
        <div class="card-left">
          <!-- Explanations Section inside the left side (blue part) -->
          <h1 class="title-white">SHACL DASHBOARD</h1>
          <div class="explanation-section">
            <p class="explanation-header">
              1. Load the graphs into <a href="https://virtuoso.openlinksw.com/" target="_blank" class="link">Virtuoso</a>
            </p>
          </div>
          <div class="explanation-section">
            <p class="explanation-header">2. Enter your Information on the right:</p>
            <div class="indented-section">
              <p class="explanation-highlight">Directory Path:</p>
              <p class="explanation-text">Input the directory path of your Virtuoso folder</p>
              <p class="explanation-highlight">Shapes Graph Name:</p>
              <p class="explanation-text">Input the name of your SHACL shapes graph</p>
              <p class="explanation-highlight">Validation Report Name:</p>
              <p class="explanation-text">Input the name of your validation report</p>
            </div>
            <div class="important-limitation">
              <p class="limitation-header">Important:</p>
              <p class="limitation-text">Each Property Shape belongs to one Node Shape.</p>
            </div>
          </div>
        </div>
          
        <!-- Right side of the card (contains title and input form) -->
        <div class="card-right">
          <h1 class="title">Hello, {{ greeting }}!</h1>
          
          <!-- New Information Form Below the Title -->
          <div class="input-card">
            <form>
              <h2 class="input-card-title">Enter Information</h2>
              
              <!-- Vuetify Input fields for directory path, shapes graph name, and validation report name -->
              <v-text-field
                v-model="directoryPath"
                label="Directory Path"
                placeholder="Enter directory path"
                class="information-field"
                outlined
                dense
              />
              
              <v-text-field
                v-model="shapesGraphName"
                label="Shapes Graph Name"
                placeholder="Enter shapes graph name"
                class="information-field"
                outlined
                dense
              />
              
              <v-text-field
                v-model="validationReportName"
                label="Validation Report Name"
                placeholder="Enter validation report name"
                class="information-field"
                outlined
                dense
              />
              
              <!-- Repositioned Enter button inside the input card -->
              <v-btn
                class="enter-btn"
                color="primary"
                @click="goToHome"
                rounded
                block
              >
                ENTER
              </v-btn>
            </form>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps, ref } from 'vue'
  
  // Props will be passed to indicate which page is active
  const props = defineProps({
    handleEnterClick: Function
  })
  
  
  // Define models for Vuetify inputs
  const directoryPath = ref('')
  const shapesGraphName = ref('')
  const validationReportName = ref('')

  // Reactive variable for the title
  const greeting = ref('');

  // Determine the greeting based on the current time
  const updateGreeting = () => {
    const currentHour = new Date().getHours();

    if (currentHour >= 5 && currentHour < 12) {
      greeting.value = 'Good Morning';
    } else if (currentHour >= 12 && currentHour < 17) {
      greeting.value = 'Good Day';
    } else if (currentHour >= 17 && currentHour < 21) {
      greeting.value = 'Good Evening';
    } else {
      greeting.value = 'Good Night';
    }
  };

  // Run the updateGreeting function when the component is created
  updateGreeting();

  const goToHome = () => {
    props.handleEnterClick(); // Change isLandingPage state to false, navigate to the main layout
  };
  </script>
  
  <style scoped>
  .landing-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(145deg, #f5f7fa 0%, #e4e7eb 100%);
    font-family: 'Inter', sans-serif;
    padding: 20px;
  }
  
  .card {
    display: flex;
    width: 100%;
    max-width: 1000px;
    min-height: 600px;
    border-radius: 24px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
    background: white;
    overflow: hidden;
  }
  
  .card-left {
    flex: 1.2;
    background: linear-gradient(145deg, #4171b9 0%, #5b8dd6 100%);
    padding: 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  
  .title-white {
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 60px;
    letter-spacing: -0.5px;
    text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3); /* Subtle shadow for better readability */
  }

  .link {
    color: inherit; /* Inherits the text color for seamless integration */
    font-weight: 700; /* Bold for emphasis */
    text-decoration: none; /* Removes underline for a cleaner look */
    border-bottom: 2px solid rgba(255, 255, 255, 0.3); /* Adds a subtle underline effect */
    padding-bottom: 2px; /* Adjusts spacing between the text and the underline */
    transition: border-color 0.3s ease; /* Smooth transition for hover effect */
  }

  .link:hover {
    border-bottom-color: rgba(255, 255, 255, 0.6); /* Changes underline color on hover */
  }
    
  .card-right {
    flex: 0.8;
    background-color: white;
    padding: 60px 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start; /* Align content to the left */
  }
  
  .title {
    font-size: 2rem; /* Original size */
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 60px; /* Match the vertical spacing with title-white */
    transform: translateY(-6px); /* Adjust positioning slightly for alignment */
  }
  
  .explanation-header {
    font-size: 1.5rem; /* Slightly larger than regular text for emphasis */
    font-weight: 600; /* Semi-bold for prominence */
    color: #ffffff; /* White text for consistency with the background */
    line-height: 1.8;
    margin-bottom: 16px; /* Adds spacing between the header and following content */
    text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3); /* Subtle shadow for better readability */
  }
  
  .explanation-highlight {
    font-size: 1.25rem;
    font-weight: 700; /* Bold text */
    color: #ffffff;
    line-height: 2;
    margin-bottom: 0px;
    text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.3); /* Subtle shadow for emphasis */
  }
  
  .indented-section {
    margin-left: 20px; /* Adjust the indentation */
    padding-left: 10px; /* Optional: Add padding for a softer indentation */
    border-left: 2px solid rgba(255, 255, 255, 0.5); /* Optional: Add a subtle left border for visual separation */
  }
  
  .explanation-text {
    font-size: 1.25rem;
    color: rgba(255, 255, 255, 0.9);
    line-height: 2;
    margin-bottom: 24px;
    font-weight: 400;
  }
  
  .input-card {
    width: 100%;
  }
  
  .input-card-title {
    font-size: 1.25rem;
    font-weight: 500;
    color: #4a5568;
    margin-bottom: 30px;
  }
  
  /* Style Vuetify inputs */
  :deep(.v-text-field) {
    margin-bottom: 24px !important;
  }
  
  :deep(.v-text-field--outlined fieldset) {
    border-color: #e2e8f0 !important;
    border-radius: 12px !important;
  }
  
  :deep(.v-text-field--outlined:hover fieldset) {
    border-color: #cbd5e0 !important;
  }
  
  /* Enter button styling */
  .enter-btn {
    margin-top: 32px !important;
    height: 48px !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    background: #4171b9 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
  }
  
  .enter-btn:hover {
    background: #5b8dd6 !important;
    box-shadow: 0 4px 12px rgba(65, 113, 185, 0.2) !important;
  }
  
  @media (max-width: 768px) {
    .card {
      flex-direction: column;
      margin: 20px;
    }
  
    .card-left,
    .card-right {
      display: flex;
      flex-direction: column;
      justify-content: flex-start; /* Align items at the top */
      gap: 20px; /* Add spacing between elements */
    }
  
    .title-white {
      font-size: 2rem;
      margin-bottom: 40px;
    }
  
    .title {
      font-size: 2rem; /* Keep original size */
      margin-bottom: 40px;
    }
  
    .explanation-text {
      font-size: 1.1rem;
      line-height: 1.8;
    }
  }

  .important-limitation {
  background: rgba(255, 255, 255, 0.2); /* Light transparent white for the background */
  padding: 16px; /* Add some spacing around the content */
  border-left: 4px solid #ff6f61; /* Highlighted border on the left */
  border-radius: 8px; /* Rounded corners for softer look */
  margin: 16px 0; /* Add spacing above and below */
  text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.1); /* Subtle shadow for readability */
}

.limitation-header {
  font-size: 1.5rem; /* Larger font size for emphasis */
  font-weight: 700; /* Bold text */
  color: #ffffff; /* White color */
  margin-bottom: 8px; /* Spacing between header and text */
}

.limitation-text {
  font-size: 1.16rem; /* Slightly smaller than the header */
  font-weight: 400; /* Regular font weight */
  color: rgba(255, 255, 255, 0.9); /* Slightly transparent white */
  line-height: 1.6; /* Better line spacing for readability */
}
  </style>
  
