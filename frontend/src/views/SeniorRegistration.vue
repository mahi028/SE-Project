<template>
  <div>
    <h2>Senior Citizen Registration</h2>

    <Stepper v-model:activeStep="activeStep" linear>
      <StepList>
        <StepItem title="Personal Info" />
        <StepItem title="Health Info" />
        <StepItem title="Contact & Emergency" />
        <StepItem title="Documents" />
        <StepItem title="Review & Submit" />
      </StepList>
    </Stepper>

    <!-- Step 0: Personal Info -->
    <div v-if="activeStep === 0" class="form-card">
      <p class="section-title">Personal Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>Full Name</label>
          <InputText v-model="formData.fullName" class="w-full" :class="{ 'p-invalid': submitted && !formData.fullName }" />
          <small v-if="submitted && !formData.fullName" class="p-error">Full Name is required.</small>
        </div>
        <div class="field col-12 md:col-3">
          <label>Date of Birth</label>
          <Calendar v-model="formData.dob" class="col-12" showIcon dateFormat="yy-mm-dd" :class="{ 'p-invalid': submitted && !formData.dob }" />
          <small v-if="submitted && !formData.dob" class="p-error">DOB is required.</small>
        </div>
        <div class="field col-12 md:col-3">
          <label>Gender</label>
          <div class="flex gap-2">
            <div class="flex align-items-center" v-for="option in ['Male', 'Female', 'Other']" :key="option">
              <RadioButton :inputId="option" :value="option" v-model="formData.gender" />
              <label :for="option" class="ml-2">{{ option }}</label>
            </div>
          </div>
          <small v-if="submitted && !formData.gender" class="p-error">Gender is required.</small>
        </div>
      </div>
      <div class="text-right">
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 1: Health Info -->
    <div v-if="activeStep === 1" class="form-card">
      <p class="section-title">Health Information</p>
      <div class="grid formgrid">
        <div class="field col-12">
          <label>Existing Medical Conditions</label>
          <Textarea v-model="formData.medicalConditions" class="w-full" rows="4" />
        </div>
        <div class="field col-12">
          <label>Medications</label>
          <Textarea v-model="formData.medications" class="w-full" rows="4" />
        </div>
        <div class="field col-12">
          <label>Allergies</label>
          <Textarea v-model="formData.allergies" class="w-full" rows="4" />
        </div>
      </div>
      <div class="text-right">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 2: Contact & Emergency -->
    <div v-if="activeStep === 2" class="form-card">
      <p class="section-title">Contact & Emergency Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>Phone Number</label>
          <InputText v-model="formData.phone" class="w-full" :class="{ 'p-invalid': submitted && !formData.phone }" />
          <small v-if="submitted && !formData.phone" class="p-error">Phone is required.</small>
        </div>
        <div class="field col-12 md:col-6">
          <label>Email</label>
          <InputText v-model="formData.email" class="w-full" type="email" disabled />
        </div>
        <div class="field col-12 md:col-6">
          <label>Emergency Contact Name</label>
          <InputText v-model="formData.emergency.name" class="w-full" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Emergency Contact Phone</label>
          <InputText v-model="formData.emergency.phone" class="w-full" />
        </div>
      </div>
      <div class="text-right">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 3: Documents -->
    <div v-if="activeStep === 3" class="form-card">
      <p class="section-title">Document Uploads</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>ID Proof (PDF)</label>
          <InputText v-model="formData.documents.idProof" class="w-full" placeholder="Upload ID Proof Filename" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Medical Report (Optional)</label>
          <InputText v-model="formData.documents.medicalReport" class="w-full" placeholder="Upload Medical Report Filename" />
        </div>
        <div class="field col-12">
          <label>Passport Photo</label>
          <InputText v-model="formData.documents.passportPhoto" class="w-full" placeholder="Passport Photo Filename" />
        </div>
      </div>
      <div class="text-right">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 4: Review -->
    <div v-if="activeStep === 4" class="form-card text-center">
      <p class="section-title">Review & Submit</p>
      <p>Click submit to complete your registration.</p>
      <div class="text-right">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Reset" class="p-button-secondary mr-2" @click="resetForm" />
        <Button label="Submit" class="p-button-success" @click="submitSenior" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Calendar from 'primevue/calendar'
import RadioButton from 'primevue/radiobutton'
import Button from 'primevue/button'
import Stepper from 'primevue/stepper'
import StepList from 'primevue/steplist'
import StepItem from 'primevue/stepitem'

const activeStep = ref(0)
const submitted = ref(false)

const formData = reactive({
  fullName: '', dob: '', gender: '', email: 'abcd@gmail.com', phone: '',
  medicalConditions: '', medications: '', allergies: '',
  emergency: { name: '', phone: '' },
  documents: { idProof: '', medicalReport: '', passportPhoto: '' }
})

onMounted(() => {
  const storedEmail = localStorage.getItem('email')
  if (storedEmail) formData.email = storedEmail
})

function nextStep() {
  if (activeStep.value < 4) activeStep.value++
}
function prevStep() {
  if (activeStep.value > 0) activeStep.value--
}
function resetForm() {
  Object.assign(formData, {
    fullName: '', dob: '', gender: '', email: formData.email, phone: '',
    medicalConditions: '', medications: '', allergies: '',
    emergency: { name: '', phone: '' },
    documents: { idProof: '', medicalReport: '', passportPhoto: '' }
  })
  submitted.value = false
  activeStep.value = 0
}
function submitSenior() {
  submitted.value = true
  if (formData.fullName && formData.dob && formData.gender && formData.phone) {
    console.log('Submitted Senior Form Data:', JSON.stringify(formData, null, 2))
    alert('Senior Registration Submitted!')
    resetForm()
  }
}
</script>

<style scoped>
.form-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-top: 1.5rem;
}
.section-title {
  font-size: 1.25rem;
  margin-bottom: 1rem;
  font-weight: 600;
}
.p-error {
  font-size: 0.85rem;
  color: red;
}
.text-right {
  text-align: right;
}
</style>
