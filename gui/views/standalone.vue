<template lang="pug">
div
  div
    h2 Stand-alone
    p.has-text-weight-bold A stand-alone agent
    p The stand-alone agent is a program that can easily be deployed on any computer.
      | It will execute adversary emulation exercises without needing to connect to a C2 server.
  hr
  div
    .columns
      .column.is-4.buttons.m-0.is-flex.is-justify-content-flex-start
        button.button.is-primary.is-small.level-item(@click="showModal = true")
          span.icon
            i.fas.fa-plus
          span Package a stand-alone agent (Calder-alone)

  // Modal
  div.modal(:class="{ 'is-active': showModal }")
    div.modal-background(@click="showModal = false")
    div.modal-card
      header.modal-card-head
        p.modal-card-title Package Stand-alone Agent
        button.delete(@click="showModal = false", aria-label="close")
      section.modal-card-body
        // Display a loading indicator while the request is in progress
        div(v-if="loading" class="has-text-centered")
          button.button.is-loading.is-large.is-light.disabled Loading...
        form#standAloneForm(v-else)
          .field
            label.label Adversary
            .control
              .select.is-fullwidth(:class="{ 'is-danger': !selectedAdversary && showErrors }")
                select(name="adversary" v-model="selectedAdversary")
                  option(value="" disabled) Select an adversary
                  option(v-for="adversary in adversaries" :key="adversary.adversary_id" :value="adversary.adversary_id")
                    | {{ adversary.name }}
              p.help.is-danger(v-if="!selectedAdversary && showErrors") Adversary is required
          .field
            label.label Fact Source
            .control
              .select.is-fullwidth(:class="{ 'is-danger': !selectedSource && showErrors }")
                select(name="factSource" v-model="selectedSource")
                  option(value="" disabled) Select a fact source
                  option(v-for="source in sources" :key="source.source_id" :value="source.source_id")
                    | {{ source.name }}
              p.help.is-danger(v-if="!selectedSource && showErrors") Fact Source is required
          .field
            label.label Planner
            .control
              .select.is-fullwidth(:class="{ 'is-danger': !selectedPlanner && showErrors }")
                select(name="planner" v-model="selectedPlanner")
                  option(value="" disabled) Select a planner
                  option(v-for="planner in planners" :key="planner.planner_id" :value="planner.planner_id")
                    | {{ planner.name }}
              p.help.is-danger(v-if="!selectedPlanner && showErrors") Planner is required
          .field
            label.label Platform
            .control
              .select.is-fullwidth(:class="{ 'is-danger': !platform && showErrors }")
                select(name="platform" id="platformSelect" v-model="platform" @change="handlePlatformChange")
                  option(value="windows") Windows
                  option(value="linux") Linux
              p.help.is-danger(v-if="!platform && showErrors") Platform is required
          .field
            label.label Extension
            .control
              .select.is-fullwidth(:class="{ 'is-danger': !extension && showErrors }")
                select(name="extension" v-model="extension")
                  option(value=".tar.gz") .tar.gz
                  option(value=".zip") .zip
              p.help.is-danger(v-if="!extension && showErrors") Extension is required
          .field
            label.label Executors
            .control
              // Executor checkboxes for Linux
              .executor-options(v-if="platform === 'linux'")
                label.checkbox.executor-checkbox
                  input(type="checkbox" name="executors" value="sh" v-model="executors")
                  | sh
                label.checkbox.executor-checkbox
                  input(type="checkbox" name="executors" value="proc" v-model="executors")
                  | proc
              // Executor checkboxes for Windows
              .executor-options(v-if="platform === 'windows'")
                label.checkbox.executor-checkbox
                  input(type="checkbox" name="executors" value="pwsh" v-model="executors")
                  | pwsh
                label.checkbox.executor-checkbox
                  input(type="checkbox" name="executors" value="psh" v-model="executors")
                  | psh
                label.checkbox.executor-checkbox
                  input(type="checkbox" name="executors" value="cmd" v-model="executors")
                  | cmd
                label.checkbox.executor-checkbox
                  input(type="checkbox" name="executors" value="proc" v-model="executors")
                  | proc
              p.help.is-danger(v-if="executors.length === 0 && showErrors") At least one executor is required
      footer.modal-card-foot
        button.button.is-success(@click="submitForm") Save
        button.button(@click="showModal = false") Cancel
</template>

<script>
export default {
  inject: ["$api"],
  data() {
    return {
      showModal: false,
      showErrors: false, // Control for error messages
      loading: false, // Control for loading state
      adversaries: [], // Will hold the fetched adversaries
      selectedAdversary: "", // Selected adversary
      sources: [], // Will hold the fetched fact sources
      selectedSource: "", // Selected fact source
      planners: [], // Will hold the fetched planners
      selectedPlanner: "", // Selected planner
      platform: "windows", // Default platform
      extension: ".tar.gz", // Default extension
      executors: [] // Selected executors
    };
  },
  methods: {
    loadAdversaries() {
      console.log('Starting API request to fetch adversaries...');
      this.$api.get('/plugin/standalone/get_adversaries')
        .then(response => {
          console.log('API Response for adversaries:', response);
          const adversaryData = response.data;
          console.log('Adversary Data:', adversaryData);
          if (adversaryData && adversaryData.adversaries) {
            this.adversaries = adversaryData.adversaries;
            console.log('Adversaries successfully loaded:', this.adversaries);
          } else {
            console.warn('Unexpected data format for adversaries:', adversaryData);
          }
        })
        .catch(error => {
          console.error('Error loading adversaries:', error);
        });
    },
    loadSources() {
      console.log('Starting API request to fetch fact sources...');
      this.$api.get('/plugin/standalone/get_sources')
        .then(response => {
          console.log('API Response for sources:', response);
          const sourceData = response.data;
          console.log('Source Data:', sourceData);
          if (sourceData && sourceData.sources) {
            this.sources = sourceData.sources;
            console.log('Sources successfully loaded:', this.sources);
          } else {
            console.warn('Unexpected data format for sources:', sourceData);
          }
        })
        .catch(error => {
          console.error('Error loading sources:', error);
        });
    },
    loadPlanners() {
      console.log('Starting API request to fetch planners...');
      this.$api.get('/plugin/standalone/get_planners')
        .then(response => {
          console.log('API Response for planners:', response);
          const plannerData = response.data;
          console.log('Planner Data:', plannerData);
          if (plannerData && plannerData.planners) {
            this.planners = plannerData.planners;
            console.log('Planners successfully loaded:', this.planners);
          } else {
            console.warn('Unexpected data format for planners:', plannerData);
          }
        })
        .catch(error => {
          console.error('Error loading planners:', error);
        });
    },
    handlePlatformChange() {
      // Clear executors when platform changes
      this.executors = [];
    },
    submitForm() {
      // Validate all fields
      this.showErrors = true;
      if (
        !this.selectedAdversary ||
        !this.selectedSource ||
        !this.selectedPlanner ||
        !this.platform ||
        !this.extension ||
        this.executors.length === 0
      ) {
        console.log('Validation failed, please fill all the required fields.');
        return;
      }

      // Construct request body
      const requestBody = {
        adversary_id: this.selectedAdversary,
        planner_id: this.selectedPlanner,
        source_id: this.selectedSource,
        platform: this.platform,
        extension: this.extension,
        executors: this.executors
      };

      console.log('Validation passed, submitting form...', requestBody);

      // Set loading state to true before sending request
      this.loading = true;

      // Send POST request with the form data
      this.$api.post('/plugin/standalone/download', requestBody, { responseType: 'blob' })
        .then(response => {
          console.log('Form submitted successfully:', response);

          // Create a new blob object from the response data
          const blob = new Blob([response.data], { type: 'application/octet-stream' });

          // Create a link element
          const link = document.createElement('a');
          link.href = window.URL.createObjectURL(blob);

          // Set the download attribute with a filename
          link.download = `standalone-agent${this.extension}`;

          // Append link to the body
          document.body.appendChild(link);

          // Programmatically click the link to trigger the download
          link.click();

          // Remove the link after download
          document.body.removeChild(link);

          this.showModal = false;
          this.showErrors = false;
        })
        .catch(error => {
          console.error('Error submitting form:', error);
        })
        .finally(() => {
          // Set loading state to false after request completes
          this.loading = false;
        });
    }
  },
  mounted() {
    this.loadAdversaries(); // Load adversaries when component is mounted
    this.loadSources(); // Load fact sources when component is mounted
    this.loadPlanners(); // Load planners when component is mounted
  }
};
</script>

<style scoped>
/* Scoped styles for the component */
.modal.is-active {
  display: flex;
}
.executor-checkbox {
  margin-right: 15px; /* Adds space between checkboxes */
}
.is-danger {
  border-color: red; /* Makes border red if there's an error */
}
</style>
