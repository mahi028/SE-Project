<template>
  <div>
    <h2>Doctor Registration</h2>

    <!-- Personal Information -->
    <div class="form-card">
      <p class="section-title">Personal Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>Full Name</label>
          <InputText v-model="doctor.fullName" class="w-full" :class="{'p-invalid': submitted && !doctor.fullName}" />
          <small v-if="submitted && !doctor.fullName" class="p-error">Full Name is required.</small>
        </div>
        <div class="field col-12 md:col-3">
          <label>DOB</label>
          <Calendar v-model="doctor.dob" class="w-full" showIcon dateFormat="yy-mm-dd" :class="{'p-invalid': submitted && !doctor.dob}" />
          <small v-if="submitted && !doctor.dob" class="p-error">DOB is required.</small>
        </div>
        <div class="field col-12 md:col-3">
          <label>Gender</label>
          <div class="flex gap-2">
            <div class="flex align-items-center">
              <RadioButton inputId="male" value="Male" v-model="doctor.gender" />
              <label for="male" class="ml-2">Male</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton inputId="female" value="Female" v-model="doctor.gender" />
              <label for="female" class="ml-2">Female</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton inputId="other" value="Other" v-model="doctor.gender" />
              <label for="other" class="ml-2">Other</label>
            </div>
          </div>
          <small v-if="submitted && !doctor.gender" class="p-error">Gender is required.</small>
        </div>
        <div class="field col-12 md:col-6">
          <label>Contact Number</label>
          <InputText v-model="doctor.contact" class="w-full" :class="{'p-invalid': submitted && !doctor.contact}" />
          <small v-if="submitted && !doctor.contact" class="p-error">Contact Number is required.</small>
        </div>
        <div class="field col-12 md:col-6">
          <label>Email</label>
          <InputText v-model="doctor.email" class="w-full" type="email" :class="{'p-invalid': submitted && !doctor.email}" />
          <small v-if="submitted && !doctor.email" class="p-error">Email is required.</small>
        </div>
      </div>
    </div>

    <!-- Professional Info -->
    <div class="form-card">
      <p class="section-title">Professional Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>License Number</label>
          <InputText v-model="doctor.licenseNumber" class="w-full" :class="{'p-invalid': submitted && !doctor.licenseNumber}" />
          <small v-if="submitted && !doctor.licenseNumber" class="p-error">License Number is required.</small>
        </div>
        <div class="field col-12 md:col-6">
          <label>Specialisation</label>
          <InputText v-model="doctor.specialisation" class="w-full" :class="{'p-invalid': submitted && !doctor.specialisation}" />
          <small v-if="submitted && !doctor.specialisation" class="p-error">Specialisation is required.</small>
        </div>
      </div>
    </div>

    <!-- Affiliation -->
    <div class="form-card">
      <p class="section-title">Affiliation</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>Hospital/Clinic Name</label>
          <InputText v-model="doctor.affiliation.name" class="w-full" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Address</label>
          <InputText v-model="doctor.affiliation.address" class="w-full" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Official Email</label>
          <InputText v-model="doctor.affiliation.email" class="w-full" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Working Hours</label>
          <InputText v-model="doctor.affiliation.hours" class="w-full" />
        </div>
        <div class="field col-12">
          <label>Availability (Days)</label>
          <InputText v-model="doctor.affiliation.days" class="w-full" />
        </div>
      </div>
    </div>

    <!-- Qualifications -->
    <div class="form-card">
      <p class="section-title">Qualifications</p>
      <div v-for="(q, index) in doctor.qualifications" :key="index" class="grid formgrid align-items-end">
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
          <Button icon="pi pi-trash" severity="danger" @click="doctor.qualifications.splice(index, 1)" v-if="doctor.qualifications.length > 1" />
        </div>
      </div>
      <Button label="Add Qualification" @click="doctor.qualifications.push({ name: '', year: '', institute: '' })" />
    </div>

    <!-- Documents Upload -->
    <div class="form-card">
      <p class="section-title">Document Uploads</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>ID Proof (PDF)</label>
          <InputText v-model="doctor.documents.idProof" class="w-full" placeholder="Upload ID Proof Filename" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Medical License (PDF)</label>
          <InputText v-model="doctor.documents.licenseCert" class="w-full" placeholder="Upload License Filename" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Qualification Certificates (PDF)</label>
          <InputText v-model="doctor.documents.qualificationCerts" class="w-full" placeholder="List of Certificates" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Passport Photo</label>
          <InputText v-model="doctor.documents.passportPhoto" class="w-full" placeholder="Passport Photo Filename" />
        </div>
      </div>
    </div>

    <div class="form-card text-right">
      <Button label="Reset" class="p-button-secondary mr-2" @click="resetDoctor" />
      <Button label="Submit" class="p-button-success" @click="submitDoctor" />
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import InputText from 'primevue/inputtext'
import Calendar from 'primevue/calendar'
import RadioButton from 'primevue/radiobutton'
import Button from 'primevue/button'

const submitted = ref(false)

const doctor = reactive({
  fullName: '', dob: '', gender: '', contact: '', email: '',
  licenseNumber: '', specialisation: '',
  affiliation: { name: '', address: '', email: '', hours: '', days: '' },
  qualifications: [ { name: '', year: '', institute: '' } ],
  documents: {
    idProof: '', licenseCert: '', qualificationCerts: '', passportPhoto: ''
  }
})

function resetDoctor() {
  doctor.fullName = ''
  doctor.dob = ''
  doctor.gender = ''
  doctor.contact = ''
  doctor.email = ''
  doctor.licenseNumber = ''
  doctor.specialisation = ''
  doctor.affiliation = { name: '', address: '', email: '', hours: '', days: '' }
  doctor.qualifications = [ { name: '', year: '', institute: '' } ]
  doctor.documents = {
    idProof: '', licenseCert: '', qualificationCerts: '', passportPhoto: ''
  }
  submitted.value = false
}

function submitDoctor() {
  submitted.value = true
  if (
    doctor.fullName && doctor.dob && doctor.gender &&
    doctor.contact && doctor.email && doctor.licenseNumber && doctor.specialisation
  ) {
    console.log('Doctor Registration:', doctor)
    alert('Doctor Registration Submitted!')
    resetDoctor()
  }
}
</script>

<style scoped>
.form-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem;
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
</style>

