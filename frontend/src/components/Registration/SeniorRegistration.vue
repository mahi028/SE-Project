<template>
  <div>
    <h2>Senior Citizen Registration</h2>

    <!-- Personal Information -->
    <div class="form-card">
      <p class="section-title">Personal Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label>Full Name</label>
          <InputText v-model="senior.fullName" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>DOB</label>
          <Calendar v-model="senior.dob" class="w-full" showIcon dateFormat="yy-mm-dd" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Gender</label>
          <div class="flex gap-2">
            <div class="flex align-items-center">
              <RadioButton inputId="male" value="Male" v-model="senior.gender" />
              <label for="male" class="ml-2">Male</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton inputId="female" value="Female" v-model="senior.gender" />
              <label for="female" class="ml-2">Female</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton inputId="other" value="Other" v-model="senior.gender" />
              <label for="other" class="ml-2">Other</label>
            </div>
          </div>
        </div>
        <div class="field col-12 md:col-6">
          <label>Address</label>
          <InputText v-model="senior.address" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Pincode</label>
          <InputText v-model="senior.pincode" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Preferred Language</label>
          <InputText v-model="senior.language" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label>Primary Phone</label>
          <InputText v-model="senior.primaryPhone" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label>Alternate Phone</label>
          <InputText v-model="senior.altPhone" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label>Email</label>
          <InputText v-model="senior.email" class="w-full" type="email" />
        </div>
      </div>
    </div>

    <!-- Emergency Contacts -->
    <div class="form-card">
      <p class="section-title">Emergency Contacts</p>
      <div v-for="(contact, index) in senior.emergencyContacts" :key="index" class="grid formgrid align-items-end">
        <div class="field col-12 md:col-3">
          <label>Name</label>
          <InputText v-model="contact.name" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Relationship</label>
          <InputText v-model="contact.relationship" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Phone Number</label>
          <InputText v-model="contact.phone" class="w-full" />
        </div>
        <div class="field col-12 md:col-2">
          <label>Alternate Phone</label>
          <InputText v-model="contact.altPhone" class="w-full" />
        </div>
        <div class="field col-12 md:col-1">
          <Button icon="pi pi-trash" severity="danger" @click="senior.emergencyContacts.splice(index, 1)" v-if="senior.emergencyContacts.length > 1" />
        </div>
      </div>
      <Button label="Add Contact" @click="senior.emergencyContacts.push({ name: '', relationship: '', phone: '', altPhone: '' })" />
    </div>

    <!-- Healthcare Professionals -->
    <div class="form-card">
      <p class="section-title">Healthcare Professionals</p>
      <div v-for="(hp, index) in senior.healthcareProfessionals" :key="index" class="grid formgrid align-items-end">
        <div class="field col-12 md:col-3">
          <label>Name</label>
          <InputText v-model="hp.name" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Clinic/Hospital</label>
          <InputText v-model="hp.clinic" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Phone Number</label>
          <InputText v-model="hp.phone" class="w-full" />
        </div>
        <div class="field col-12 md:col-2">
          <label>Speciality</label>
          <InputText v-model="hp.speciality" class="w-full" />
        </div>
        <div class="field col-12 md:col-1">
          <Button icon="pi pi-trash" severity="danger" @click="senior.healthcareProfessionals.splice(index, 1)" v-if="senior.healthcareProfessionals.length > 1" />
        </div>
      </div>
      <Button label="Add Professional" @click="senior.healthcareProfessionals.push({ name: '', clinic: '', phone: '', speciality: '' })" />
    </div>

    <!-- Insurance -->
    <div class="form-card">
      <p class="section-title">Insurance</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-3">
          <label>Insurance Company</label>
          <InputText v-model="senior.insurance.company" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Policy/Member ID</label>
          <InputText v-model="senior.insurance.policyId" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Valid Upto</label>
          <Calendar v-model="senior.insurance.validity" class="w-full" showIcon dateFormat="yy-mm-dd" />
        </div>
        <div class="field col-12 md:col-3">
          <label>Billing Contact</label>
          <InputText v-model="senior.insurance.billingContact" class="w-full" />
        </div>
      </div>
    </div>

    <div class="form-card text-right">
      <Button label="Reset" class="p-button-warning mr-2" @click="resetForm" />
      <Button label="Back" class="p-button-secondary mr-2" @click="$emit('back')" />
      <Button label="Submit Senior Registration" class="p-button-success" @click="submitSenior" />
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import InputText from 'primevue/inputtext'
import Calendar from 'primevue/calendar'
import RadioButton from 'primevue/radiobutton'
import Button from 'primevue/button'

const initialSenior = () => ({
  fullName: '', dob: '', gender: '', address: '', pincode: '',
  language: '', primaryPhone: '', altPhone: '', email: '',
  emergencyContacts: [ { name: '', relationship: '', phone: '', altPhone: '' } ],
  healthcareProfessionals: [ { name: '', clinic: '', phone: '', speciality: '' } ],
  insurance: { company: '', policyId: '', validity: '', billingContact: '' }
})

const senior = reactive(initialSenior())

function submitSenior() {
  console.log('Senior Registration:', senior)
  alert('Senior Registration Submitted!')
}

function resetForm() {
  Object.assign(senior, initialSenior())
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
</style>

