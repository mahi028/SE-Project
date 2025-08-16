<script setup>
import { ref, reactive, computed } from 'vue';
import { useMutation } from '@vue/apollo-composable';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import gql from 'graphql-tag';

// --- constants / factories ---
const STEP_COUNT = 6;
const daysOfWeek = Object.freeze([
  { name: 'Monday' }, { name: 'Tuesday' }, { name: 'Wednesday' },
  { name: 'Thursday' }, { name: 'Friday' }, { name: 'Saturday' }, { name: 'Sunday' }
]);

// new: specialization options
const specializationOptions = Object.freeze([
  'General Medicine','Cardiology','Neurology','Pediatrics','Orthopedics',
  'Dermatology','Psychiatry','Oncology','Radiology','Emergency Medicine',
  'Endocrinology','Gastroenterology','Other'
]);

const createInitialFormData = () => ({
  dob: '',
  gender: '',
  licenseNumber: '',
  licenseAuthority: '',
  licenseValidUpto: null,
  // replaced single specialisation string with multiselect + other field
  specialisations: [],
  otherSpecialisation: '',
  affiliation: {
    name: '',
    address: '',
    email: '',
    hoursFrom: '',
    hoursTo: '',
    days: []
  },
  // new doctor meta fields required by AddDoctor
  pincode: '',
  alternatePhoneNum: '',
  experience: '',
  consultationFee: '',
  appointmentWindow: '',
  qualifications: [{ id: crypto.randomUUID(), name: '', year: '', institute: '' }],
  documents: {
    idProof: null,
    licenseCert: null,
    qualificationCerts: null,
    passportPhoto: null
  }
});

const formData = reactive(createInitialFormData());
const activeStep = ref(0);
const submitted = ref(false);
const errors = ref({});
const route = useRouter()

// GraphQL mutation aligned with backend AddDoctor (snake_case args)
const ADD_DOCTOR_MUTATION = gql`
  mutation AddDoctor(
    $licenseNumber: String!
    $gender: String
    $dob: DateTime
    $address: String
    $pincode: String
    $alternatePhoneNum: String
    $specialization: String
    $affiliation: JSONString
    $qualification: JSONString
    $experience: Int
    $consultationFee: Float
    $workingHours: String
    $availability: JSONString
    $documents: JSONString
    $appointmentWindow: Int
  ) {
    addDoctor(
      licenseNumber: $licenseNumber
      gender: $gender
      dob: $dob
      address: $address
      pincode: $pincode
      alternatePhoneNum: $alternatePhoneNum
      specialization: $specialization
      affiliation: $affiliation
      qualification: $qualification
      experience: $experience
      consultationFee: $consultationFee
      workingHours: $workingHours
      availability: $availability
      documents: $documents
      appointmentWindow: $appointmentWindow
    ) {
      status
      message
    }
  }
`;

const toast = useToast();
const { mutate: addDoctor, loading: submitting } = useMutation(ADD_DOCTOR_MUTATION);

// --- validation logic ---
function validateStep(step) {
  const stepErrors = {};
  switch (step) {
    case 0:
      if (!formData.dob) stepErrors.dob = 'DOB required';
      if (!formData.gender) stepErrors.gender = 'Gender required';
      break;
    case 1:
      if (!formData.licenseNumber) stepErrors.licenseNumber = 'License Number required';
      if (!formData.licenseAuthority) stepErrors.licenseAuthority = 'Issuing Authority required';
      if (!formData.licenseValidUpto) stepErrors.licenseValidUpto = 'Validity date required';
      // updated specialisation validation
      const pickedNonOther = formData.specialisations.filter(s => s !== 'Other');
      if (pickedNonOther.length === 0 && !formData.otherSpecialisation.trim()) {
        stepErrors.specialisations = 'At least one specialization required';
      }
      if (formData.specialisations.includes('Other') && !formData.otherSpecialisation.trim()) {
        stepErrors.otherSpecialisation = 'Please specify the other specialization';
      }
      break;
    case 2:
      // optional for now; left blank intentionally
      break;
    case 3:
      if (!formData.qualifications.length) {
        stepErrors.qualifications = 'At least one qualification required';
      } else {
        formData.qualifications.forEach((q, i) => {
          if (!q.name || !q.year || !q.institute) {
            stepErrors[`qualification_${i}`] = 'All fields required';
          }
        });
      }
      break;
    case 4:
      // document presence can be enforced later
      break;
    default:
      break;
  }
  errors.value = stepErrors;
  return Object.keys(stepErrors).length === 0;
}

const currentStepValid = computed(() => validateStep(activeStep.value));
const isFirstStep = computed(() => activeStep.value === 0);
const isLastStep = computed(() => activeStep.value === STEP_COUNT - 1);

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
    errors.value = {};
    submitted.value = false;
  }
}

function addQualification() {
  formData.qualifications.push({ id: crypto.randomUUID(), name: '', year: '', institute: '' });
}

function removeQualification(index) {
  if (formData.qualifications.length > 1) formData.qualifications.splice(index, 1);
}

function onSelect(event, field) {
  const file = event.files?.[0];
  if (file) formData.documents[field] = file;
}

function resetForm() {
  Object.assign(formData, createInitialFormData());
  activeStep.value = 0;
  submitted.value = false;
  errors.value = {};
}

// helper to derive a single specialization string
const specializationString = () => {
  const core = formData.specialisations.filter(s => s !== 'Other');
  if (formData.specialisations.includes('Other') && formData.otherSpecialisation.trim()) {
    core.push(formData.otherSpecialisation.trim());
  }
  return core.join(', ');
};

// helper function to format time for display and backend
const formatTimeForBackend = (timeValue) => {
  if (!timeValue) return null;
  // timeValue is a Date object from PrimeVue Calendar
  const hours = timeValue.getHours().toString().padStart(2, '0');
  const minutes = timeValue.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
};

function submitDoctor() {
  submitted.value = true;
  // validate all steps (reuse step validator)
  for (let s = 0; s < STEP_COUNT - 1; s++) {
    if (!validateStep(s)) {
      activeStep.value = s;
      return;
    }
  }

  // Format working hours properly
  const fromTime = formatTimeForBackend(formData.affiliation.hoursFrom);
  const toTime = formatTimeForBackend(formData.affiliation.hoursTo);
  const workingHours = (fromTime && toTime) ? `${fromTime} - ${toTime}` : null;

  const vars = {
    licenseNumber: formData.licenseNumber,
    gender: formData.gender || null,
    dob: formData.dob ? new Date(formData.dob).toISOString() : null,
    address: formData.affiliation.address || null,
    pincode: formData.pincode || null,
    alternatePhoneNum: formData.alternatePhoneNum || null,
    specialization: specializationString() || null,
    affiliation: JSON.stringify({
      name: formData.affiliation.name,
      email: formData.affiliation.email,
      hoursFrom: fromTime,
      hoursTo: toTime
    }),
    qualification: JSON.stringify(formData.qualifications.map(q => ({
      name: q.name, year: q.year, institute: q.institute
    }))),
    experience: formData.experience ? Number(formData.experience) : null,
    consultationFee: formData.consultationFee ? Number(formData.consultationFee) : null,
    workingHours: workingHours,
    availability: JSON.stringify(formData.affiliation.days.map(d => d.name || d)),
    documents: JSON.stringify(
      Object.fromEntries(
        Object.entries(formData.documents).map(([k, v]) => [k, v ? (v.name || v) : null])
      )
    ),
    appointmentWindow: formData.appointmentWindow ? Number(formData.appointmentWindow) : null
  };

  addDoctor(vars).then(({ data }) => {
    const res = data?.add_doctor;
    if (res?.status === 201) {
      toast.add({ severity: 'success', summary: 'Success', detail: res.message, life: 3000 });
      resetForm();
      route.push({ name: 'Doctordashboard' })
    } else {
      toast.add({ severity: 'error', summary: 'Error', detail: res?.message || 'Failed', life: 4000 });
    }
  }).catch(err => {
    console.error(err);
    toast.add({ severity: 'error', summary: 'Error', detail: 'Submission failed', life: 4000 });
  });
}
</script>

<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-semibold text-surface-900 dark:text-surface-0">Doctor Registration</h2>

    <Stepper v-model:activeStep="activeStep" linear class="bg-transparent">
      <StepList>
        <StepItem title="Personal Info" />
        <StepItem title="Professional Info" />
        <StepItem title="Affiliation" />
        <StepItem title="Qualifications" />
        <StepItem title="Documents" />
        <StepItem title="Review" />
      </StepList>
    </Stepper>

    <!-- Step 0 -->
    <div v-if="activeStep === 0" class="form-card">
      <p class="section-title">Personal Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-4">
          <label for="dob">DOB</label>
          <Calendar id="dob" v-model="formData.dob" class="w-100 compact-input" showIcon dateFormat="yy-mm-dd"
            :class="{ 'p-invalid': submitted && errors.dob }" />
          <small v-if="submitted && errors.dob" class="p-error">{{ errors.dob }}</small>
        </div>
        <div class="field col-12 md:col-3">
          <label>Gender</label>
          <div class="flex gap-3 flex-wrap">
            <div class="flex items-center" v-for="option in ['Male','Female','Other']" :key="option">
              <RadioButton :inputId="`gender-${option}`" :value="option" v-model="formData.gender" />
              <label :for="`gender-${option}`" class="ml-2">{{ option }}</label>
            </div>
          </div>
          <small v-if="submitted && errors.gender" class="p-error">{{ errors.gender }}</small>
        </div>
      </div>
      <div class="actions">
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" />
      </div>
    </div>

    <!-- Step 1 -->
    <div v-else-if="activeStep === 1" class="form-card">
      <p class="section-title">Professional Information</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label for="licenseNumber">License Number</label>
          <InputText id="licenseNumber" v-model="formData.licenseNumber" class="w-full"
            :class="{ 'p-invalid': submitted && errors.licenseNumber }" />
          <small v-if="submitted && errors.licenseNumber" class="p-error">{{ errors.licenseNumber }}</small>
        </div>
        <div class="field col-12 md:col-6">
          <label for="licenseAuthority">License Issuing Authority</label>
          <InputText id="licenseAuthority" v-model="formData.licenseAuthority" class="w-full"
            :class="{ 'p-invalid': submitted && errors.licenseAuthority }" />
          <small v-if="submitted && errors.licenseAuthority" class="p-error">{{ errors.licenseAuthority }}</small>
        </div>
        <div class="field col-12 md:col-6">
          <label for="licenseValidUpto">Valid Upto</label>
          <Calendar id="licenseValidUpto" v-model="formData.licenseValidUpto" class="w-100 compact-input" showIcon dateFormat="yy-mm-dd"
            :class="{ 'p-invalid': submitted && errors.licenseValidUpto }" />
          <small v-if="submitted && errors.licenseValidUpto" class="p-error">{{ errors.licenseValidUpto }}</small>
        </div>

        <!-- replaced single InputText with MultiSelect + conditional other field -->
        <div class="field col-12 md:col-6">
          <label for="specialisations">Specialisations</label>
          <MultiSelect
            id="specialisations"
            v-model="formData.specialisations"
            :options="specializationOptions"
            placeholder="Select specialisations"
            display="chip"
            class="w-full"
            :class="{ 'p-invalid': submitted && errors.specialisations }"
          />
          <small v-if="submitted && errors.specialisations" class="p-error">{{ errors.specialisations }}</small>
          <div v-if="formData.specialisations.includes('Other')" class="mt-2">
            <InputText
              id="otherSpecialisation"
              v-model="formData.otherSpecialisation"
              placeholder="Specify other specialization"
              class="w-full"
              :class="{ 'p-invalid': submitted && errors.otherSpecialisation }"
            />
            <small v-if="submitted && errors.otherSpecialisation" class="p-error">{{ errors.otherSpecialisation }}</small>
          </div>
        </div>
      </div>
      <div class="actions">
        <Button label="Back" severity="secondary" @click="prevStep" />
        <Button label="Next" :disabled="!currentStepValid" @click="nextStep" />
      </div>
    </div>

    <!-- Step 2 -->
    <div v-else-if="activeStep === 2" class="form-card">
      <p class="section-title">Affiliation & Practice</p>
      <div class="grid formgrid">
        <!-- existing affiliation fields -->
        <div class="field col-12 md:col-6">
          <label for="affName">Hospital / Clinic Name</label>
          <InputText id="affName" v-model="formData.affiliation.name" class="w-full" />
        </div>
        <div class="field col-12 md:col-6">
          <label for="affAddr">Address</label>
          <InputText id="affAddr" v-model="formData.affiliation.address" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label for="pincode">Pincode</label>
          <InputText id="pincode" v-model="formData.pincode" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label for="altPhone">Alternate Phone</label>
          <InputText id="altPhone" v-model="formData.alternatePhoneNum" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label for="affEmail">Official Email</label>
          <InputText id="affEmail" v-model="formData.affiliation.email" class="w-full" />
        </div>
        <div class="field col-12 md:col-6 flex flex-wrap gap-3">
          <Calendar v-model="formData.affiliation.hoursFrom" timeOnly hourFormat="24" showIcon placeholder="From" class="flex-1 compact-input" />
          <Calendar v-model="formData.affiliation.hoursTo" timeOnly hourFormat="24" showIcon placeholder="To" class="flex-1 compact-input" />
        </div>
        <div class="field col-12 md:col-6">
          <label>Availability (Days)</label>
          <MultiSelect v-model="formData.affiliation.days" :options="daysOfWeek" optionLabel="name"
            placeholder="Select available days" display="chip" class="w-full md:w-20rem" />
        </div>
        <div class="field col-12 md:col-4">
          <label for="experience">Experience (Years)</label>
          <InputText id="experience" v-model="formData.experience" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label for="fee">Consultation Fee</label>
          <InputText id="fee" v-model="formData.consultationFee" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label for="apptWindow">Appointment Window (min)</label>
          <InputText id="apptWindow" v-model="formData.appointmentWindow" class="w-full" />
        </div>
      </div>
      <div class="actions">
        <Button label="Back" severity="secondary" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 3 -->
    <div v-else-if="activeStep === 3" class="form-card">
      <p class="section-title">Qualifications</p>
      <div v-for="(q, index) in formData.qualifications" :key="q.id" class="grid formgrid align-items-end">
        <div class="field col-12 md:col-4">
          <label :for="`qualName-${q.id}`">Qualification Name</label>
          <InputText :id="`qualName-${q.id}`" v-model="q.name" class="w-full" />
        </div>
        <div class="field col-12 md:col-3">
          <label :for="`qualYear-${q.id}`">Year</label>
          <InputText :id="`qualYear-${q.id}`" v-model="q.year" class="w-full" />
        </div>
        <div class="field col-12 md:col-4">
          <label :for="`qualInst-${q.id}`">Institute</label>
          <InputText :id="`qualInst-${q.id}`" v-model="q.institute" class="w-full" />
        </div>
        <div class="field col-12 md:col-1 flex justify-end">
          <Button v-if="formData.qualifications.length > 1" icon="pi pi-trash" severity="danger"
            @click="removeQualification(index)" />
        </div>
      </div>
      <small v-if="submitted && errors.qualifications" class="p-error">{{ errors.qualifications }}</small>
      <div class="mt-3 flex gap-2">
        <Button label="Add Qualification" icon="pi pi-plus" outlined @click="addQualification" />
      </div>
      <div class="actions">
        <Button label="Back" severity="secondary" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 4 -->
    <div v-else-if="activeStep === 4" class="form-card">
      <p class="section-title">Document Uploads</p>
      <div class="grid formgrid">
        <div class="field col-12 md:col-6">
          <label for="idProof">ID Proof (PDF)</label>
          <FileUpload mode="basic" name="idProof" accept=".pdf" chooseLabel="Choose File" customUpload
            @select="onSelect($event, 'idProof')" />
        </div>
        <div class="field col-12 md:col-6">
          <label for="licenseCert">Medical License (PDF)</label>
          <FileUpload mode="basic" name="licenseCert" accept=".pdf" chooseLabel="Choose File" customUpload
            @select="onSelect($event, 'licenseCert')" />
        </div>
        <div class="field col-12 md:col-6">
          <label for="qualificationCerts">Qualification Certificates (PDF)</label>
          <FileUpload mode="basic" name="qualificationCerts" accept=".pdf" chooseLabel="Choose File" customUpload
            @select="onSelect($event, 'qualificationCerts')" />
        </div>
        <div class="field col-12 md:col-6">
          <label for="passportPhoto">Passport Photo</label>
            <FileUpload mode="basic" name="passportPhoto" accept="image/*" chooseLabel="Choose File" customUpload
              @select="onSelect($event, 'passportPhoto')" />
        </div>
      </div>
      <div class="actions">
        <Button label="Back" severity="secondary" @click="prevStep" />
        <Button label="Next" @click="nextStep" />
      </div>
    </div>

    <!-- Step 5 -->
    <div v-else-if="activeStep === 5" class="form-card">
      <p class="section-title">Review & Submit</p>
      <p class="text-sm mb-4 text-surface-600 dark:text-surface-300">
        Review the entered information then submit your application.
      </p>
      <!-- Summary (minimal for now) -->
      <ul class="text-sm space-y-1 mb-6">
        <li>
          <strong>Specialisations:</strong>
          {{
            (formData.specialisations.filter(s => s !== 'Other')).concat(
              formData.specialisations.includes('Other') && formData.otherSpecialisation
                ? [formData.otherSpecialisation]
                : []
            ).join(', ') || '—'
          }}
        </li>
        <li><strong>License #:</strong> {{ formData.licenseNumber || '—' }}</li>
        <li><strong>Experience:</strong> {{ formData.experience || '—' }}</li>
        <li><strong>Consultation Fee:</strong> {{ formData.consultationFee || '—' }}</li>
        <li><strong>Appt Window:</strong> {{ formData.appointmentWindow || '—' }}</li>
        <li><strong>Pincode:</strong> {{ formData.pincode || '—' }}</li>
        <li>
          <strong>Working Hours:</strong>
          {{
            (formatTimeForBackend(formData.affiliation.hoursFrom) && formatTimeForBackend(formData.affiliation.hoursTo))
              ? `${formatTimeForBackend(formData.affiliation.hoursFrom)} - ${formatTimeForBackend(formData.affiliation.hoursTo)}`
              : '—'
          }}
        </li>
        <li>
          <strong>Available Days:</strong>
          {{ formData.affiliation.days.map(d => d.name || d).join(', ') || '—' }}
        </li>
      </ul>
      <div class="actions">
        <Button label="Back" severity="secondary" @click="prevStep" />
        <Button label="Reset" severity="secondary" outlined @click="resetForm" />
        <Button label="Submit" severity="success" :disabled="submitting" :loading="submitting" @click="submitDoctor" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* layout & density */
.form-card {
  @apply bg-surface-0 dark:bg-surface-900 text-surface-900 dark:text-surface-0 rounded-xl shadow-sm border border-surface-200 dark:border-surface-700;
  padding: 1.1rem; /* reduced from larger padding */
}
@media (min-width: 768px) {
  .form-card {
    padding: 1.35rem;
  }
}
h2 {
  font-size: 2.4rem; /* increased from existing utility size */
}
.section-title {
  @apply font-semibold border-b border-surface-200 dark:border-surface-700;
  font-size: 1.2rem; /* was 1.05rem */
  margin: 0 0 .9rem 0;
  padding-bottom: .4rem;
}
.field {
  margin-bottom: 0.9rem;
}
.field label {
  @apply font-medium text-surface-700 dark:text-surface-200;
  font-size: .95rem; /* was .82rem */
  margin-bottom: .25rem;
  display: block;
}
:deep(.p-inputtext),
:deep(.p-multiselect),
.compact-input :deep(.p-inputtext),
.compact-input :deep(input),
.compact-input :deep(.p-multiselect-label) {
  font-size: .9rem; /* was .78-.8rem */
}
.compact-input :deep(.p-calendar) {
  width: 100%;
}
.compact-input :deep(.p-icon) {
  width: 0.9rem;
  height: 0.9rem;
}
:deep(.p-password input),
:deep(.p-inputtext) {
  padding: .55rem .7rem;
  font-size: .8rem;
}
:deep(.p-multiselect) {
  font-size: .78rem;
}
.actions :deep(button),
:deep(.p-button) {
  font-size: .8rem; /* was .7rem */
  padding: .45rem .9rem;
}
.p-error {
  @apply text-red-500;
  font-size: .75rem; /* was .65rem */
  margin-top: .15rem;
}
ul.text-sm {
  font-size: .85rem; /* was .75rem */
}
.actions {
  @apply flex gap-2 justify-end;
  margin-top: .75rem;
}
</style>
