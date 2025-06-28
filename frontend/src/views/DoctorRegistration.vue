<template>
  <div>
    <h2>Doctor Registration</h2>

    <Stepper v-model:activeStep="activeStep" linear>
      <StepList>
        <StepItem title="Personal Info" />
        <StepItem title="Professional Info" />
        <StepItem title="Affiliation" />
        <StepItem title="Qualifications" />
        <StepItem title="Documents" />
        <StepItem title="Review & Submit" />
      </StepList>
    </Stepper>

    <!-- Step 0: Personal Information -->
    <div v-if="activeStep === 0" class="form-card">
      <p class="section-title">Personal Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>Full Name</label>
          <InputText v-model="formData.fullName" class="w-full" :class="{'p-invalid': submitted && !formData.fullName}" />
          <small v-if="submitted && !formData.fullName" class="p-error">Full Name is required.</small>
        </div>
        <div class="field col-12 md:col-4">
          <label>DOB</label>
          <Calendar v-model="formData.dob" class="w-half" showIcon dateFormat="yy-mm-dd" :class="{'p-invalid': submitted && !formData.dob}" />
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
        <div class="field col-12 md:col-6">
          <label>Contact Number</label>
          <InputText v-model="formData.contact" class="w-full" :class="{'p-invalid': submitted && !formData.contact}" />
          <small v-if="submitted && !formData.contact" class="p-error">Contact Number is required.</small>
        </div>
        <div class="field col-12 md:col-6">
          <label>Email</label>
          <InputText v-model="formData.email" class="w-full" type="email" disabled />
        </div>
      </div>
      <div class="text-right">
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 1: Professional Info -->
    <div v-if="activeStep === 1" class="form-card">
      <p class="section-title">Professional Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>License Number</label>
          <InputText v-model="formData.licenseNumber" class="w-full" :class="{'p-invalid': submitted && !formData.licenseNumber}" />
          <small v-if="submitted && !formData.licenseNumber" class="p-error">License Number is required.</small>
        </div>
        <div class="field col-12 md:col-6">
          <label>License Issuing Authority</label>
          <InputText v-model="formData.licenseAuthority" class="w-full" :class="{'p-invalid': submitted && !formData.licenseAuthority}" />
          <small v-if="submitted && !formData.licenseAuthority" class="p-error">Issuing Authority is required.</small>
        </div>
        <div class="field col-12 md:col-6">
          <label>Valid Upto</label>
          <Calendar v-model="formData.licenseValidUpto" showIcon dateFormat="yy-mm-dd" class="w-full" :class="{'p-invalid': submitted && !formData.licenseValidUpto}" />
          <small v-if="submitted && !formData.licenseValidUpto" class="p-error">Validity Date is required.</small>
        </div>
        <div class="field col-12 md:col-6">
          <label>Specialisation</label>
          <InputText v-model="formData.specialisation" class="w-full" :class="{'p-invalid': submitted && !formData.specialisation}" />
          <small v-if="submitted && !formData.specialisation" class="p-error">Specialisation is required.</small>
        </div>
      </div>
      <div class="text-right">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 2: Affiliation -->
    <div v-if="activeStep === 2" class="form-card">
      <p class="section-title">Affiliation</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>Hospital/Clinic Name</label>
          <InputText v-model="formData.affiliation.name" class="w-full" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Address</label>
          <InputText v-model="formData.affiliation.address" class="w-full" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Official Email</label>
          <InputText v-model="formData.affiliation.email" class="w-full" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Working Hours</label>
          <InputText v-model="formData.affiliation.hours" class="w-full" />
        </div>
        <div class="field col-12">
          <label>Availability (Days)</label>
          <InputText v-model="formData.affiliation.days" class="w-full" />
        </div>
      </div>
      <div class="text-right">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 3: Qualifications -->
    <div v-if="activeStep === 3" class="form-card">
      <p class="section-title">Qualifications</p>
      <div v-for="(q, index) in formData.qualifications" :key="index" class="grid formgrid align-items-end">
        <div class="field col-12 md:col-4">
          <label>Qualification Name</label>
          <InputText v-model="q.name" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label>Year of Completion</label>
          <InputText v-model="q.year" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Institute</label>
          <InputText v-model="q.institute" class="w-full" />
        </div>
        <div class="field col-12 md:col-1">
          <Button icon="pi pi-trash" severity="danger" @click="formData.qualifications.splice(index, 1)" v-if="formData.qualifications.length > 1" />
        </div>
      </div>
      <Button label="Add Qualification" @click="formData.qualifications.push({ name: '', year: '', institute: '' })" />
      <div class="text-right mt-4">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 4: Document Uploads -->
    <div v-if="activeStep === 4" class="form-card">
      <p class="section-title">Document Uploads</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>ID Proof (PDF)</label>
          <InputText v-model="formData.documents.idProof" class="w-full" placeholder="Upload ID Proof Filename" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Medical License (PDF)</label>
          <InputText v-model="formData.documents.licenseCert" class="w-full" placeholder="Upload License Filename" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Qualification Certificates (PDF)</label>
          <InputText v-model="formData.documents.qualificationCerts" class="w-full" placeholder="List of Certificates" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Passport Photo</label>
          <InputText v-model="formData.documents.passportPhoto" class="w-full" placeholder="Passport Photo Filename" />
        </div>
      </div>
      <div class="text-right">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 5: Review & Submit -->
    <div v-if="activeStep === 5" class="form-card text-center">
      <p class="section-title">Review & Submit</p>
      <p>Click submit to complete your registration.</p>
      <div class="text-right">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Reset" class="p-button-secondary mr-2" @click="resetForm" />
        <Button label="Submit" class="p-button-success" @click="submitDoctor" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import InputText from 'primevue/inputtext'
import Calendar from 'primevue/calendar'
import RadioButton from 'primevue/radiobutton'
import Button from 'primevue/button'
import Stepper from 'primevue/stepper'
import StepList from 'primevue/steplist'
import StepItem from 'primevue/stepitem'

const activeStep = ref(0)
const submitted = ref(false)

const formData = reactive({
  fullName: '', dob: '', gender: '', contact: '', email: 'abcd@gmail.com',
  licenseNumber: '', licenseAuthority: '', licenseValidUpto: null, specialisation: '',
  affiliation: { name: '', address: '', email: '', hours: '', days: '' },
  qualifications: [{ name: '', year: '', institute: '' }],
  documents: { idProof: '', licenseCert: '', qualificationCerts: '', passportPhoto: '' }
})

onMounted(() => {
  const storedEmail = localStorage.getItem('email')
  if (storedEmail) formData.email = storedEmail
})

function nextStep() {
  if (activeStep.value < 5) activeStep.value++
}
function prevStep() {
  if (activeStep.value > 0) activeStep.value--
}
function resetForm() {
  Object.assign(formData, {
    fullName: '', dob: '', gender: '', contact: '', email: formData.email,
    licenseNumber: '', licenseAuthority: '', licenseValidUpto: null, specialisation: '',
    affiliation: { name: '', address: '', email: '', hours: '', days: '' },
    qualifications: [{ name: '', year: '', institute: '' }],
    documents: { idProof: '', licenseCert: '', qualificationCerts: '', passportPhoto: '' }
  })
  submitted.value = false
  activeStep.value = 0
}
function submitDoctor() {
  submitted.value = true
  if (
    formData.fullName && formData.dob && formData.gender &&
    formData.contact && formData.licenseNumber && formData.specialisation
  ) {
    console.log('Submitted Form Data:', JSON.stringify(formData, null, 2))
    alert('Doctor Registration Submitted!')
    resetForm()
  }
}
</script>

<style scoped>
.form-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
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
