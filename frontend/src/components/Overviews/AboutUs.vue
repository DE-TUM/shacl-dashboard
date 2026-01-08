<template>
    <div>
      <!-- Title Section -->
      <div class="page-title">
        <h1>Data Engineering Group</h1>
        <h1>Technical University of Munich</h1>
      </div>
  
      <!-- About Us Section -->
      <div class="about-us-wrapper">
        <div class="about-us-container" ref="containerRef">
          <!-- SVG for Connections -->
          <svg class="connections-svg" ref="svgRef"></svg>
  
          <!-- Professor Card -->
          <div
            class="person-card professor-card"
            :style="{ top: `${professorY}%`, left: `${professorX}%` }"
          >
            <ExternalLink
              :href="professor.link"
              aria-label="Navigate to Professor Maribel Acosta's profile"
            >
              <PersonCard
                :photo="professor.photo"
                :name="professor.name"
                :role="professor.role"
              />
            </ExternalLink>
          </div>
  
          <!-- Doctoral Students Cards -->
          <div
            v-for="(student, index) in doctoralStudents"
            :key="index"
            class="person-card student-card"
            :style="{ top: `${student.y}%`, left: `${student.x}%` }"
          >
            <ExternalLink
              :href="student.link"
              :aria-label="`Navigate to ${student.name}'s profile`"
            >
              <PersonCard
                :photo="student.photo"
                :name="student.name"
                :role="student.role"
              />
            </ExternalLink>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
/**
 * AboutUs component
 *
 * Displays information about the team, project, and purpose of the SHACL Dashboard application.
 * Contains sections for team members, project goals, and contact information.
 *
 * @example
 * // Basic usage in a parent component template:
 * // <AboutUs />
 *
 * @prop {Array} [teamMembers=[]] - List of team members to display
 * @prop {String} [contactEmail=''] - Contact email address
 * @prop {String} [projectDescription=''] - Description of the project
 *
 * @dependencies
 * - vue (Composition API)
 *
 * @style
 * - Clean, responsive layout for presenting about information.
 * - Sections for different types of content (team, project, contact).
 * - May include images, links, and formatted text blocks.
 * 
 * @returns {HTMLElement} A visually appealing about page showing the Data Engineering Group
 * at Technical University of Munich, featuring a professor and doctoral students arranged
 * hierarchically with SVG connection lines between them, representing supervision relationships.
 */
  import ExternalLink from "../Reusable/ExternalLink.vue"; // Adjust the path as necessary
  import { onMounted, ref, onBeforeUnmount, nextTick } from "vue";
  import * as d3 from 'd3';
  import PersonCard from "../Reusable/PersonCard.vue";
  
  // References to DOM elements
  const containerRef = ref(null);
  const svgRef = ref(null);
  
  // Professor data with link
  const professor = {
    name: "Prof. Dr. Maribel Acosta",
    role: "Professor",
    photo: "img/m.png",
    link: "https://www.cs.cit.tum.de/cde/people/maribel-acosta/",
  };
  
  // Doctoral students data with links (positions in percentages)
  const doctoralStudents = [
    {
      name: "Jin Ke",
      role: "Doctoral Student",
      photo: "img/ji.png",
      x: 15,
      y: 80,
      link: "https://www.cs.cit.tum.de/cde/people/jin-ke/",
    },
    {
      name: "Johannes Maekelburg",
      role: "Doctoral Student",
      photo: "img/jo.png",
      x: 50,
      y: 80,
      link: "https://www.cs.cit.tum.de/cde/people/johannes-maekelburg/",
    },
    {
      name: "Zenon Zacouris",
      role: "Doctoral Student",
      photo: "img/z.png",
      x: 85,
      y: 80,
      link: "https://www.cs.cit.tum.de/cde/people/zenon-zacouris/",
    },
  ];
  
  // Coordinates for the professor card (in percentages)
  const professorX = 50;
  const professorY = 20;
  
  /**
   * Function to calculate intersection points at the borders
   * @param {Object} sourceBox - Bounding box of the source element
   * @param {Object} targetBox - Bounding box of the target element
   * @returns {Object} - Contains sourceEdge, targetEdge, and angleDeg
   */
  const calculateIntersection = (sourceBox, targetBox) => {
    // Calculate centers
    const sourceCenter = {
      x: sourceBox.x + sourceBox.width / 2,
      y: sourceBox.y + sourceBox.height / 2,
    };
    const targetCenter = {
      x: targetBox.x + targetBox.width / 2,
      y: targetBox.y + targetBox.height / 2,
    };
  
    // Calculate angle between centers
    const angle = Math.atan2(targetCenter.y - sourceCenter.y, targetCenter.x - sourceCenter.x);
  
    // Convert angle to degrees for label rotation
    let angleDeg = angle * (180 / Math.PI);
  
    // Adjust angle to prevent upside-down text
    if (angleDeg > 90 || angleDeg < -90) {
      angleDeg -= 180;
    }
  
    // Calculate radii
    const sourceRadius = Math.min(sourceBox.width, sourceBox.height) / 2;
    const targetRadius = Math.min(targetBox.width, targetBox.height) / 2;
  
    // Calculate intersection points on the borders
    const sourceEdge = {
      x: sourceCenter.x + sourceRadius * Math.cos(angle),
      y: sourceCenter.y + sourceRadius * Math.sin(angle),
    };
    const targetEdge = {
      x: targetCenter.x - targetRadius * Math.cos(angle),
      y: targetCenter.y - targetRadius * Math.sin(angle),
    };
  
    return { sourceEdge, targetEdge, angleDeg };
  };
  
  /**
   * Function to draw connections using D3.js
   */
  const drawConnections = () => {
    const svg = d3.select(svgRef.value);
    const container = containerRef.value;
  
    // Check if container exists
    if (!container) {
      console.error("Container element not found.");
      return;
    }
  
    const width = container.clientWidth;
    const height = container.clientHeight;
  
    svg
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", `0 0 ${width} ${height}`)
      .style("position", "absolute")
      .style("top", 0)
      .style("left", 0)
      .style("z-index", -1); // Ensure SVG is below the cards
  
    // Clear previous drawings
    svg.selectAll("*").remove();
  
    // Define arrowhead marker with precise alignment
    svg.append("defs").append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "-0 -5 10 10")
      .attr("refX", 10) // Adjusted to 10 for better alignment
      .attr("refY", 0)
      .attr("orient", "auto")
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("markerUnits", "userSpaceOnUse") // Allows precise placement
      .attr("xoverflow", "visible")
      .append("svg:path")
      .attr("d", "M 0,-5 L 10 ,0 L 0,5")
      .attr("fill", "#888")
      .style("stroke", "none");
  
    // Get container's bounding box
    const containerBox = container.getBoundingClientRect();
  
    // Get professor's bounding box relative to the container
    const professorCard = container.querySelector(".professor-card");
    if (!professorCard) {
      console.error("Professor card not found.");
      return;
    }
    const professorBox = professorCard.getBoundingClientRect();
    const professorRelativeBox = {
      x: professorBox.left - containerBox.left,
      y: professorBox.top - containerBox.top,
      width: professorBox.width,
      height: professorBox.height,
    };
  
    // Get student cards
    const studentCards = container.querySelectorAll(".student-card");
    if (studentCards.length === 0) {
      console.error("No student cards found.");
      return;
    }
  
    // Calculate connections
    const connections = Array.from(studentCards).map((studentCard, index) => {
      const studentBox = studentCard.getBoundingClientRect();
      const studentRelativeBox = {
        x: studentBox.left - containerBox.left,
        y: studentBox.top - containerBox.top,
        width: studentBox.width,
        height: studentBox.height,
      };
  
      const { sourceEdge, targetEdge, angleDeg } = calculateIntersection(professorRelativeBox, studentRelativeBox);
  
      return {
        source: sourceEdge,
        target: targetEdge,
        label: ":isSupervisedBy", // Removed colon if not needed
        targetName: doctoralStudents[index].name,
        angleDeg,
      };
    });
  
    // Draw lines with arrowheads
    svg.selectAll("line")
      .data(connections)
      .enter()
      .append("line")
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y)
      .attr("stroke", "#888")
      .attr("stroke-width", 2)
      .attr("marker-end", "url(#arrowhead)")
      .attr("aria-label", d => `${professor.name} ${d.label} ${d.targetName}`);
  
    // Draw rotated labels
    svg.selectAll("text")
      .data(connections)
      .enter()
      .append("text")
      .attr("x", d => (d.source.x + d.target.x) / 2)
      .attr("y", d => (d.source.y + d.target.y) / 2 - 13) // Increased offset by 2px (from -11 to -13)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#555")
      .attr("transform", d => {
        const midX = (d.source.x + d.target.x) / 2;
        const midY = (d.source.y + d.target.y) / 2 - 7; // Match the y attribute
        return `rotate(${d.angleDeg}, ${midX}, ${midY})`;
      })
      .text(d => d.label);
  };
  
  /**
   * Lifecycle Hooks
   */
  onMounted(async () => {
    await nextTick(); // Ensure DOM elements are rendered
    drawConnections();
    window.addEventListener("resize", drawConnections);
  });
  
  onBeforeUnmount(() => {
    window.removeEventListener("resize", drawConnections);
  });
  </script>
  

 <style scoped>
 /* Title Section Styling */
 .page-title {
   text-align: center; /* Centers the text horizontally */
   margin-bottom: 40px; /* Adds space between the title and the cards */
 }
 
 .page-title h1 {
   font-size: 2.5rem; /* Makes the text large */
   margin: 10px 0; /* Adds vertical spacing between the titles */
   color: #333; /* Optional: Sets a dark color for better readability */
   font-weight: bold; /* Optional: Makes the text bold */
 }
 
 /* Wrapper to center the about-us-container */
 .about-us-wrapper {
   display: flex;
   justify-content: center;
   align-items: center;
   width: 100%;
   padding: 40px 20px; /* Adds spacing around the container */
   box-sizing: border-box;
 }
 
 /* Container for the About Us section */
 .about-us-container {
   position: relative;
   width: 1000px; /* Fixed width for alignment */
   max-height: 600px; /* Set maximum height to 600px */
   min-height: 600px; /* Ensure a consistent height */
   max-width: 100%;
   background-color: #f9f9f9; /* Optional: Background color for visibility */
   border: 1px solid #ddd; /* Optional: Border for container */
   border-radius: 8px; /* Optional: Rounded corners */
   box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Optional: Shadow for depth */
   overflow: hidden; /* Ensures child elements don't overflow */
   z-index: 0; /* Base stacking context */
 }
 
 /* SVG Layer */
 .svg-layer {
   position: absolute;
   top: 0;
   left: 0;
   width: 100%;
   height: 100%;
   z-index: 1; /* Lower than cards layer */
 }
 
 .connections-svg {
   position: absolute;
   top: 0;
   left: 0;
   width: 100%;
   height: 100%;
   z-index: -1; /* Explicitly set to negative z-index */
   pointer-events: none;
 }
 
 /* Cards Layer */
 .cards-layer {
   position: relative;
   z-index: 50; /* Higher than SVG layer */
 }
 
 /* Person Cards Styling */
 .person-card {
   position: absolute;
   transform: translate(-50%, -50%); /* Center the card */
   z-index: 10; /* Higher than SVG */
   cursor: pointer;
   transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease; /* Include border-color in transition */
   border: 2px solid transparent; /* Default border */
   border-radius: 4px; /* Optional: Rounded borders for aesthetic */
 }
 
 .person-card:hover {
   transform: translate(-50%, -50%) scale(1.05); /* Slight zoom on hover */
   border-color: #0466c8ff; /* Change border color on hover */
   /* box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2); */
 }
 
 /* Link Styling */
 .person-card a {
   display: block;
   text-decoration: none;
   color: inherit; /* Inherit text color */
   position: relative;
   z-index: 30000; /* Ensure links are above cards if necessary */
 }
 
 .person-card a:focus {
   outline: 2px solid #0466c8ff; /* Visible focus state for accessibility */
   outline-offset: 2px;
 }
 
 /* Responsive Adjustments */
 @media (max-width: 1200px) {
   .about-us-container {
     width: 90%;
     min-height: 600px; /* Maintain consistent height */
   }
 }
 
 @media (max-width: 768px) {
   .about-us-container {
     width: 100%;
     max-height: 600px; /* Maintain maximum height */
     min-height: 600px; /* Ensure consistent height */
   }
 
   /* Stack students vertically on smaller screens */
   .professor-card {
     top: 100px;
     left: 50%;
   }
 
   .student-card:nth-child(2) {
     top: 500px; /* Position below the professor */
     left: 25%;
   }
 
   .student-card:nth-child(3) {
     top: 500px; /* Position below the professor */
     left: 50%;
   }
 
   .student-card:nth-child(4) {
     top: 500px; /* Position below the professor */
     left: 75%;
   }
 
   /* Note: For dynamic responsiveness, consider enhancing the drawConnections function */
 }
 </style>
