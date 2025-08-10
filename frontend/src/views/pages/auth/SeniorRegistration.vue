<script setup>
import { ref, reactive, computed } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import gql from 'graphql-tag';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';

const STEP_COUNT = 9; // was 10

const createInitialFormData = () => ({
  dob: '',
  gender: '',
  address: '',
  pincode: '',
  alternatePhoneNum: '',
  medicalConditions: [{ id: crypto.randomUUID(), name: '', diagnosedYear: '', curingYear: '', report: '' }],
  medications: [{ id: crypto.randomUUID(), name: '', dosage: '', frequency: '', route: '', startDate: '', endDate: '' }],
  vaccinations: [{ id: crypto.randomUUID(), name: '', date: '' }],
  insurance: { provider: '', memberId: '', validUpto: '', billingContact: '' },
  healthcareProvider: { Name: '', clinic: '', contact: '', email: '', specialty: '' },
  lifestyle: { smoking: '', alcohol: '', substanceUse: '', diet: '', exercise: '', livingStatus: '', caregiver: '' },
  allergies: '',
  documents: { idProof: null, medicalReport: null, passportPhoto: null }
});

const formData = reactive(createInitialFormData());
const activeStep = ref(0);
const submitted = ref(false);
const errors = ref({});

function validateStep(step) {
  const e = {};
  switch (step) {
    case 0:
      if (!formData.dob) e.dob = 'DOB required';
      if (!formData.gender) e.gender = 'Gender required';
      if (!formData.address?.trim()) e.address = 'Address required';
      if (!formData.pincode?.trim()) e.pincode = 'Pincode required';
      break;
    default:
      break;
  }
  errors.value = e;
  return Object.keys(e).length === 0;
}

const currentStepValid = computed(() => validateStep(activeStep.value));

function nextStep() {
  submitted.value = true;
  if (!validateStep(activeStep.value)) return;
  if (activeStep.value < STEP_COUNT - 1) {
    activeStep.value++;
    submitted.value = false;
    errors.value = {};
  }
}
function prevStep() {
  if (activeStep.value > 0) {
    activeStep.value--;
    submitted.value = false;
    errors.value = {};
  }
}
function resetForm() {
  Object.assign(formData, createInitialFormData());
  activeStep.value = 0;
  submitted.value = false;
  errors.value = {};
}

// GraphQL mutation (Pascal case style like DoctorRegistration.vue)
const ADD_SENIOR_MUTATION = gql`
  mutation AddSenior(
    $gender: String
    $dob: DateTime
    $address: String
    $pincode: String
    $alternatePhoneNum: String
    $medicalInfo: JSONString
  ) {
    addSenior(
      gender: $gender
      dob: $dob
      address: $address
      pincode: $pincode
      alternatePhoneNum: $alternatePhoneNum
      medicalInfo: $medicalInfo
    ) {
      status
      message
    }
  }
`;

const toast = useToast();
const router = useRouter();
const { mutate: addSenior, loading: submitting } = useMutation(ADD_SENIOR_MUTATION);

// build medicalInfo payload
function buildMedicalInfo() {
  return JSON.stringify({
    medicalConditions: formData.medicalConditions.map(c => ({
      name: c.name,
      diagnosedYear: c.diagnosedYear,
      curingYear: c.curingYear,
      report: c.report ? (c.report.name || c.report) : null
    })),
    medications: formData.medications.map(m => ({
      name: m.name, dosage: m.dosage, frequency: m.frequency, route: m.route,
      startDate: m.startDate, endDate: m.endDate
    })),
    vaccinations: formData.vaccinations.map(v => ({ name: v.name, date: v.date })),
    insurance: formData.insurance,
    healthcareProvider: formData.healthcareProvider,
    lifestyle: formData.lifestyle,
    allergies: formData.allergies,
    documents: Object.fromEntries(
      Object.entries(formData.documents).map(([k,v]) => [k, v ? (v.name || v) : null])
    )
  });
}

// replace submitSenior
function submitSenior() {
  submitted.value = true;
  for (let s = 0; s < STEP_COUNT - 1; s++) {
    if (!validateStep(s)) {
      activeStep.value = s;
      return;
    }
  }
  const vars = {
    gender: formData.gender || null,
    dob: formData.dob ? new Date(formData.dob).toISOString() : null,
    address: formData.address || null,
    pincode: formData.pincode || null,
    alternatePhoneNum: formData.alternatePhoneNum || null,
    medicalInfo: buildMedicalInfo()
  };
  addSenior(vars).then(({ data }) => {
    const res = data?.add_senior || data?.addSenior;
    if (res?.status === 201) {
      toast.add({ severity: 'success', summary: 'Success', detail: res.message, life: 3000 });
      resetForm();
      router.push({ name: 'login' });
    } else {
      toast.add({ severity: 'error', summary: 'Error', detail: res?.message || 'Submission failed', life: 4000 });
    }
  }).catch(err => {
    console.error(err);
    toast.add({ severity: 'error', summary: 'Error', detail: 'Submission failed', life: 4000 });
  });
}

// mutation hooks can be added here later
function addCondition() {
  formData.medicalConditions.push({ id: crypto.randomUUID(), name: '', diagnosedYear: '', curingYear: '', report: '' });
}
function addMedication() {
  formData.medications.push({ id: crypto.randomUUID(), name: '', dosage: '', frequency: '', route: '', startDate: '', endDate: '' });
}
function onReportUpload(event, index) {
  const file = event.files?.[0];
  if (file) formData.medicalConditions[index].report = file;
}
function onFileUpload(event, type) {
  const file = event.files?.[0];
  if (file) formData.documents[type] = file;
}
</script>

<template>
  <div class="registration-container">
    <h2 class="form-title">Senior Citizen Registration</h2>

    <Stepper v-model:activeStep="activeStep" linear class="custom-stepper">
      <StepList>
        <StepItem title="Personal Info" />
        <StepItem title="Health Info" />
        <StepItem title="Medications" />
        <StepItem title="Vaccinations" />
        <StepItem title="Insurance" />
        <StepItem title="Healthcare Provider" />
        <!-- removed Emergency Contacts -->
        <StepItem title="Lifestyle / Habits" />
        <StepItem title="Documents" />
        <StepItem title="Review & Submit" />
      </StepList>
    </Stepper>

    <!-- Step 0: Personal Info -->
    <div v-if="activeStep === 0" class="form-card">
      <p class="section-title">Personal Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-3">
          <label for="dob">Date of Birth</label>
          <Calendar id="dob" v-model="formData.dob" showIcon dateFormat="yy-mm-dd" class="w-full compact-input"
            :class="{ 'p-invalid': submitted && errors.dob }" />
          <small v-if="submitted && errors.dob" class="p-error">{{ errors.dob }}</small>
        </div>
        <div class="field col-12 md:col-3">
          <label>Gender</label>
          <div class="flex gap-3 flex-wrap">
            <div class="flex items-center" v-for="g in ['Male','Female','Other']" :key="g">
              <RadioButton :inputId="`gender-${g}`" :value="g" v-model="formData.gender" />
              <label :for="`gender-${g}`" class="ml-2">{{ g }}</label>
            </div>
          </div>
          <small v-if="submitted && errors.gender" class="p-error">{{ errors.gender }}</small>
        </div>
        <div class="field col-12 md:col-6">
          <label for="address">Address</label>
          <InputText id="address" v-model="formData.address" class="w-full"
            :class="{ 'p-invalid': submitted && errors.address }" />
          <small v-if="submitted && errors.address" class="p-error">{{ errors.address }}</small>
        </div>
        <div class="field col-12 md:col-3">
          <label for="pincode">Pincode</label>
          <InputText id="pincode" v-model="formData.pincode" class="w-full"
            :class="{ 'p-invalid': submitted && errors.pincode }" />
          <small v-if="submitted && errors.pincode" class="p-error">{{ errors.pincode }}</small>
        </div>
        <div class="field col-12 md:col-3">
          <label for="altPhone">Alternate Phone (Optional)</label>
          <InputText id="altPhone" v-model="formData.alternatePhoneNum" class="w-full" />
        </div>
      </div>
      <div class="actions">
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" />
      </div>
    </div>

    <!-- Step 1: Medical Conditions -->
    <div v-if="activeStep === 1" class="form-card">
      <p class="section-title">Medical Conditions</p>
      <div v-for="(condition, index) in formData.medicalConditions" :key="index" class="condition-container grid formgrid mb-4">
        <div class="field col-12 md:col-3">
          <label class="input-label">Condition</label>
          <InputText v-model="condition.name" class="w-full senior-input" placeholder="e.g. Asthma" />
        </div>
        <div class="field col-12 md:col-2">
          <label class="input-label">Diagnosed Year</label>
          <InputText v-model="condition.diagnosedYear" class="w-full senior-input" placeholder="YYYY" />
        </div>
        <div class="field col-12 md:col-3">
          <label class="input-label">Curing Year / Ongoing</label>
          <InputText v-model="condition.curingYear" class="w-full senior-input" placeholder="e.g. 2022 or 'Ongoing'" />
        </div>
        <div class="field col-12 md:col-3">
          <label class="input-label">Medical Report (Optional)</label>
          <FileUpload mode="basic" accept=".pdf,image/*" chooseLabel="Choose File" :auto="false"
            customUpload @select="onReportUpload($event, index)" class="senior-file-upload" />
          <small v-if="condition.report" class="block mt-1 text-sm text-green-600 file-uploaded">{{ condition.report }}</small>
        </div>
        <div class="field col-12 md:col-1 flex align-items-end">
          <Button icon="pi pi-trash" severity="danger" class="p-button-sm remove-button"
            @click="formData.medicalConditions.splice(index, 1)"
            v-if="formData.medicalConditions.length > 1" />
        </div>
      </div>
      <Button label="Add Condition" icon="pi pi-plus" class="p-button-sm mt-2 mb-4 add-button" @click="addCondition" />
      <div class="actions">
        <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" class="next-button" />
      </div>
    </div>

    <!-- Step 2: Medications -->
    <div v-if="activeStep === 2" class="form-card">
      <p class="section-title">Medications / Supplements</p>
      <div v-for="(med, index) in formData.medications" :key="index" class="medication-container grid formgrid mb-4">
        <div class="field col-12 md:col-3">
          <label class="input-label">Name</label>
          <InputText v-model="med.name" class="w-full senior-input" placeholder="e.g. Metformin" />
        </div>
        <div class="field col-12 md:col-2">
          <label class="input-label">Dosage</label>
          <InputText v-model="med.dosage" class="w-full senior-input" placeholder="e.g. 500mg" />
        </div>
        <div class="field col-12 md:col-2">
          <label class="input-label">Frequency</label>
          <InputText v-model="med.frequency" class="w-full senior-input" placeholder="e.g. Twice a day" />
        </div>
        <div class="field col-12 md:col-2">
          <label class="input-label">Route</label>
          <InputText v-model="med.route" class="w-full senior-input" placeholder="e.g. Oral" />
        </div>
        <div class="field col-12 md:col-2">
          <label class="input-label">Start Date</label>
          <Calendar v-model="med.startDate" dateFormat="yy-mm-dd" class="w-full senior-calendar" showIcon />
        </div>
        <div class="field col-12 md:col-2">
          <label class="input-label">End Date / Ongoing</label>
          <InputText v-model="med.endDate" class="w-full senior-input" placeholder="yyyy-mm-dd or 'Ongoing'" />
        </div>
        <div class="field col-12 md:col-1 flex align-items-end">
          <Button icon="pi pi-trash" severity="danger" class="p-button-sm remove-button"
            @click="formData.medications.splice(index, 1)"
            v-if="formData.medications.length > 1" />
        </div>
      </div>
      <Button label="Add Medication" icon="pi pi-plus" class="p-button-sm mt-2 mb-4 add-button" @click="addMedication" />
      <div class="field col-12">
        <label class="input-label">Allergies</label>
        <Textarea v-model="formData.allergies" class="w-full senior-textarea" rows="3"
          placeholder="List any allergies you have (medications, foods, etc.)" />
      </div>
      <div class="actions">
        <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" class="next-button" />
      </div>
    </div>

    <!-- Step 3: Vaccinations -->
    <div v-if="activeStep === 3" class="form-card">
      <p class="section-title">Vaccinations</p>
      <div class="grid formgrid">
        <div v-for="(vaccine, index) in formData.vaccinations" :key="index" class="vaccine-container grid formgrid mb-4">
          <div class="field col-12 md:col-6">
            <label class="input-label">Vaccination Name</label>
            <InputText v-model="vaccine.name" class="w-full senior-input" placeholder="e.g. COVID-19 Booster" />
          </div>
          <div class="field col-12 md:col-4">
            <label class="input-label">Vaccination Date</label>
            <Calendar v-model="vaccine.date" class="w-full senior-calendar" dateFormat="yy-mm-dd" showIcon />
          </div>
          <div class="field col-12 md:col-2 flex align-items-end">
            <Button icon="pi pi-trash" severity="danger" class="p-button-sm remove-button"
              @click="formData.vaccinations.splice(index, 1)"
              v-if="formData.vaccinations.length > 1" />
          </div>
        </div>
        <Button label="Add Vaccination" icon="pi pi-plus" class="p-button-sm mt-2 add-button"
          @click="formData.vaccinations.push({ id: crypto.randomUUID(), name: '', date: '' })" />
      </div>

      <div class="actions">
        <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" class="next-button" />
      </div>
    </div>

    <!-- Step 4: Insurance -->
    <div v-if="activeStep === 4" class="form-card">
      <p class="section-title">Insurance Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label class="input-label">Insurer / Scheme</label>
          <InputText v-model="formData.insurance.provider" class="w-full senior-input"
            placeholder="e.g. Ayushman Bharat or HDFC Ergo" />
        </div>
        <div class="field col-12 md:col-6">
          <label class="input-label">Beneficiary ID</label>
          <InputText v-model="formData.insurance.memberId" class="w-full senior-input"
            placeholder="e.g. ABC123456" />
        </div>
        <div class="field col-12 md:col-6">
          <label class="input-label">Valid Upto</label>
          <Calendar v-model="formData.insurance.validUpto" class="w-full senior-calendar"
            dateFormat="yy-mm-dd" showIcon />
        </div>
        <div class="field col-12 md:col-6">
          <label class="input-label">Billing Contact</label>
          <InputText v-model="formData.insurance.billingContact" class="w-full senior-input"
            placeholder="Phone or Email" />
        </div>
      </div>

      <div class="actions">
        <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" class="next-button" />
      </div>
    </div>

    <!-- Step 5: Healthcare Provider -->
    <div v-if="activeStep === 5" class="form-card">
      <p class="section-title">Primary Healthcare Provider</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label class="input-label">Doctor's Name</label>
          <InputText v-model="formData.healthcareProvider.Name" class="w-full senior-input"
            placeholder="e.g. Dr. Sharma" />
        </div>
        <div class="field col-12 md:col-6">
          <label class="input-label">Clinic/Hospital</label>
          <InputText v-model="formData.healthcareProvider.clinic" class="w-full senior-input"
            placeholder="e.g. City Hospital" />
        </div>
        <div class="field col-12 md:col-4">
          <label class="input-label">Contact</label>
          <InputText v-model="formData.healthcareProvider.contact" class="w-full senior-input"
            placeholder="Phone number" />
        </div>
        <div class="field col-12 md:col-4">
          <label class="input-label">Email</label>
          <InputText v-model="formData.healthcareProvider.email" class="w-full senior-input"
            placeholder="doctor@example.com" />
        </div>
        <div class="field col-12 md:col-4">
          <label class="input-label">Specialty</label>
          <Dropdown v-model="formData.healthcareProvider.specialty" :options="specialityOptions"
            placeholder="Select a Specialty" class="w-full senior-dropdown" />
        </div>
      </div>
      <div class="actions">
        <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" class="next-button" />
      </div>
    </div>

    <!-- Step 6: Lifestyle / Habits -->
    <div v-if="activeStep === 6" class="form-card">
      <p class="section-title">Lifestyle & Habits</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-4">
          <label class="input-label">Smoking</label>
          <InputText v-model="formData.lifestyle.smoking" class="w-full senior-input"
            placeholder="e.g. Never, Occasionally, Regularly" />
        </div>
        <div class="field col-12 md:col-4">
          <label class="input-label">Alcoholic</label>
          <InputText v-model="formData.lifestyle.alcohol" class="w-full senior-input"
            placeholder="e.g. No, Yes, Social Drinker" />
        </div>
        <div class="field col-12 md:col-4">
          <label class="input-label">Illicit Substance Use</label>
          <InputText v-model="formData.lifestyle.substanceUse" class="w-full senior-input"
            placeholder="e.g. No, Yes - specify" />
        </div>
        <div class="field col-12 md:col-6">
          <label class="input-label">Dietary Habits</label>
          <InputText v-model="formData.lifestyle.diet" class="w-full senior-input"
            placeholder="e.g. Vegetarian, Non-veg, Vegan" />
        </div>
        <div class="field col-12 md:col-6">
          <label class="input-label">Physical Activity</label>
          <InputText v-model="formData.lifestyle.exercise" class="w-full senior-input"
            placeholder="e.g. Regular, None, Walking" />
        </div>
        <div class="field col-12 md:col-6">
          <label class="input-label">Living Status</label>
          <InputText v-model="formData.lifestyle.livingStatus" class="w-full senior-input"
            placeholder="e.g. Alone, With Family" />
        </div>
        <div class="field col-12 md:col-6">
          <label class="input-label">Caregiver Availability</label>
          <InputText v-model="formData.lifestyle.caregiver" class="w-full senior-input"
            placeholder="e.g. Yes, No, Occasionally" />
        </div>
      </div>

      <div class="actions">
        <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" class="next-button" />
      </div>
    </div>

    <!-- Step 7: Documents -->
    <div v-if="activeStep === 7" class="form-card">
      <p class="section-title">Document Uploads</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label class="input-label">ID Proof</label>
          <FileUpload mode="basic" accept=".pdf,image/*" chooseLabel="Choose File" customUpload
            @select="onFileUpload($event, 'idProof')" class="senior-file-upload" />
          <small v-if="formData.documents.idProof" class="block mt-1 text-sm text-green-600 file-uploaded">
            {{ formData.documents.idProof }}
          </small>
        </div>

        <div class="field col-12 md:col-6">
          <label class="input-label">Medical Report</label>
          <FileUpload mode="basic" accept=".pdf,image/*" chooseLabel="Choose File" customUpload
            @select="onFileUpload($event, 'medicalReport')" class="senior-file-upload" />
          <small v-if="formData.documents.medicalReport" class="block mt-1 text-sm text-green-600 file-uploaded">
            {{ formData.documents.medicalReport }}
          </small>
        </div>

        <div class="field col-12">
          <label class="input-label">Passport Photo</label>
          <FileUpload mode="basic" accept="image/*" chooseLabel="Choose File" customUpload
            @select="onFileUpload($event, 'passportPhoto')" class="senior-file-upload" />
          <small v-if="formData.documents.passportPhoto" class="block mt-1 text-sm text-green-600 file-uploaded">
            {{ formData.documents.passportPhoto }}
          </small>
        </div>
      </div>

      <div class="actions">
        <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" />
      </div>
    </div>

    <!-- Step 8: Review & Submit -->
    <div v-if="activeStep === 8" class="form-card">
      <p class="section-title">Review & Submit</p>
      <ul class="text-sm space-y-1 mb-4">
        <li><strong>Conditions:</strong> {{ formData.medicalConditions.length }}</li>
        <li><strong>Medications:</strong> {{ formData.medications.length }}</li>
        <li><strong>Vaccinations:</strong> {{ formData.vaccinations.length }}</li>
      </ul>
      <div class="actions">
        <Button label="Back" severity="secondary" @click="prevStep" />
        <Button label="Reset" outlined severity="secondary" @click="resetForm" />
        <Button label="Submit" severity="success" :disabled="submitting" :loading="submitting" @click="submitSenior" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Replaced previous custom styles for consistency with DoctorRegistration.vue */
.form-card {
  @apply bg-surface-0 dark:bg-surface-900 text-surface-900 dark:text-surface-0 rounded-xl shadow-sm border border-surface-200 dark:border-surface-700;
  padding: 1.15rem;
}
@media (min-width: 768px) {
  .form-card { padding: 1.4rem; }
}
.section-title {
  @apply font-semibold border-b border-surface-200 dark:border-surface-700;
  font-size: 1.15rem;
  margin: 0 0 .8rem 0;
  padding-bottom: .35rem;
}
.field { margin-bottom: .85rem; }
.field label {
  @apply font-medium text-surface-700 dark:text-surface-200;
  font-size: .85rem;
  margin-bottom: .25rem;
  display: block;
}
:deep(.p-inputtext),
.compact-input :deep(.p-inputtext),
.compact-input :deep(input) {
  font-size: .85rem;
  padding: .55rem .65rem;
}
.compact-input :deep(.p-icon) { width: .9rem; height: .9rem; }
.p-error {
  @apply text-red-500;
  font-size: .65rem;
  margin-top: .2rem;
}
.actions {
  @apply flex gap-2 justify-end;
  margin-top: .9rem;
}
.actions :deep(.p-button) {
  font-size: .75rem;
  padding: .5rem .9rem;
}
ul.text-sm { font-size: .75rem; }

.senior-calendar .p-inputtext {
    font-size: 1rem;
    padding: 0.75rem;
}

.senior-radio {
    transform: scale(1.2);
    margin-right: 0.5rem;
}

.radio-label {
    font-size: 1rem;
    color: #555;
}

.gender-options {
    margin-top: 0.5rem;
}

.senior-dropdown {
    width: 100%;
}

.senior-dropdown .p-dropdown {
    width: 100%;
}

.senior-file-upload {
    width: 100%;
}

.senior-file-upload .p-button {
    width: 100%;
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    color: #555;
}

.senior-file-upload .p-button:hover {
    background-color: #e9ecef;
    border-color: #ced4da;
}

.file-uploaded {
    font-size: 0.9rem;
}

/* Buttons */
.navigation-buttons {
    display: flex;
    justify-content: flex-end;
    margin-top: 2rem;
    gap: 0.75rem;
}

.next-button, .back-button, .submit-button, .reset-button, .add-button {
    font-size: 1rem;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    transition: all 0.3s;
}

.next-button, .submit-button {
    background-color: #3498db;
    border-color: #3498db;
}

.next-button:hover, .submit-button:hover {
    background-color: #2980b9;
    border-color: #2980b9;
}

.back-button, .reset-button {
    background-color: #95a5a6;
    border-color: #95a5a6;
}

.back-button:hover, .reset-button:hover {
    background-color: #7f8c8d;
    border-color: #7f8c8d;
}

.add-button {
    background-color: #2ecc71;
    border-color: #2ecc71;
}

.add-button:hover {
    background-color: #27ae60;
    border-color: #27ae60;
}

.remove-button {
    background-color: #e74c3c;
    border-color: #e74c3c;
}

.remove-button:hover {
    background-color: #c0392b;
    border-color: #c0392b;
}

/* Error Messages */
.p-error {
    font-size: 0.85rem;
    color: #e74c3c;
    margin-top: 0.25rem;
    display: block;
}

/* Review Card */
.review-card {
    text-align: center;
    padding: 2rem;
}

.review-text {
    font-size: 1.1rem;
    color: #555;
    margin-bottom: 2rem;
    line-height: 1.6;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .form-card {
        padding: 1rem;
    }

    .section-title {
        font-size: 1.2rem;
    }

    .input-label {
        font-size: 0.9rem;
    }

    .senior-input, .senior-textarea, .senior-calendar .p-inputtext {
        font-size: 0.95rem;
        padding: 0.65rem;
    }

    .navigation-buttons {
        flex-wrap: wrap;
        justify-content: center;
    }

    .next-button, .back-button, .submit-button, .reset-button, .add-button {
        width: 100%;
        margin-bottom: 0.5rem;
    }

    .gender-options {
        flex-direction: column;
        gap: 0.5rem;
    }

    .condition-container, .medication-container, .vaccine-container, .contact-container {
        grid-template-columns: 1fr !important;
        gap: 1rem;
    }

    .remove-button {
        margin-top: 0.5rem;
    }
}

@media (max-width: 480px) {
    .form-title {
        font-size: 1.5rem;
    }

    .section-title {
        font-size: 1.1rem;
    }

    .senior-input, .senior-textarea, .senior-calendar .p-inputtext {
        font-size: 0.9rem;
        padding: 0.6rem;
    }

    .radio-label {
        font-size: 0.9rem;
    }
}
</style>
