<script setup>
import { ref, reactive, onMounted } from 'vue';

const activeStep = ref(0);
const submitted = ref(false);
const daysOfWeek = [{ name: 'Monday' }, { name: 'Tuesday' }, { name: 'Wednesday' }, { name: 'Thursday' }, { name: 'Friday' }, { name: 'Saturday' }, { name: 'Sunday' }];

const formData = reactive({
    fullName: '',
    dob: '',
    gender: '',
    contact: '',
    email: 'abcd@gmail.com',
    licenseNumber: '',
    licenseAuthority: '',
    licenseValidUpto: null,
    specialisation: '',
    affiliation: { name: '', address: '', email: '', hoursFrom: '', hoursTo: '', days: [] },
    qualifications: [{ name: '', year: '', institute: '' }],
    documents: { idProof: '', licenseCert: '', qualificationCerts: '', passportPhoto: '' }
});

onMounted(() => {
    const storedEmail = localStorage.getItem('email');
    if (storedEmail) formData.email = storedEmail;
});

function nextStep() {
    if (activeStep.value < 5) activeStep.value++;
}
function prevStep() {
    if (activeStep.value > 0) activeStep.value--;
}

function onSelect(event, field) {
    const file = event.files?.[0];
    if (file) {
        formData.documents[field] = file.name;
    }
}

function resetForm() {
    Object.assign(formData, {
        fullName: '',
        dob: '',
        gender: '',
        contact: '',
        email: formData.email,
        licenseNumber: '',
        licenseAuthority: '',
        licenseValidUpto: null,
        specialisation: '',
        affiliation: { name: '', address: '', email: '', hours: '', days: '' },
        qualifications: [{ name: '', year: '', institute: '' }],
        documents: { idProof: '', licenseCert: '', qualificationCerts: '', passportPhoto: '' }
    });
    submitted.value = false;
    activeStep.value = 0;
}
function submitDoctor() {
    submitted.value = true;
    if (formData.fullName && formData.dob && formData.gender && formData.contact && formData.licenseNumber && formData.specialisation) {
        console.log('Submitted Form Data:', JSON.stringify(formData, null, 2));
        alert('Doctor Registration Submitted!');
        resetForm();
    }
}
</script>

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
                    <InputText v-model="formData.fullName" class="w-full" :class="{ 'p-invalid': submitted && !formData.fullName }" />
                    <small v-if="submitted && !formData.fullName" class="p-error">Full Name is required.</small>
                </div>
                <div class="field col-12 md:col-4">
                    <label>DOB</label>
                    <Calendar v-model="formData.dob" class="w-half" showIcon dateFormat="yy-mm-dd" :class="{ 'p-invalid': submitted && !formData.dob }" />
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
                    <InputText v-model="formData.contact" class="w-full" :class="{ 'p-invalid': submitted && !formData.contact }" />
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
                    <InputText v-model="formData.licenseNumber" class="w-full" :class="{ 'p-invalid': submitted && !formData.licenseNumber }" />
                    <small v-if="submitted && !formData.licenseNumber" class="p-error">License Number is required.</small>
                </div>
                <div class="field col-12 md:col-6">
                    <label>License Issuing Authority</label>
                    <InputText v-model="formData.licenseAuthority" class="w-full" :class="{ 'p-invalid': submitted && !formData.licenseAuthority }" />
                    <small v-if="submitted && !formData.licenseAuthority" class="p-error">Issuing Authority is required.</small>
                </div>
                <div class="field col-12 md:col-6">
                    <label>Valid Upto</label>
                    <Calendar v-model="formData.licenseValidUpto" class="w-half" showIcon dateFormat="yy-mm-dd" :class="{ 'p-invalid': submitted && !formData.dob }" />
                    <small v-if="submitted && !formData.licenseValidUpto" class="p-error">Validity Date is required.</small>
                </div>
                <div class="field col-12 md:col-6">
                    <label>Specialisation</label>
                    <InputText v-model="formData.specialisation" class="w-full" :class="{ 'p-invalid': submitted && !formData.specialisation }" />
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

                <div class="flex flex-column md:flex-row md:gap-3">
                    <Calendar v-model="formData.affiliation.hoursFrom" timeOnly hourFormat="24" class="w-full md:w-6" placeholder="From (hh:mm)" showIcon />
                    <Calendar v-model="formData.affiliation.hoursTo" timeOnly hourFormat="24" class="w-full md:w-6" placeholder="To (hh:mm)" showIcon />
                </div>

                <div class="field col-12">
                    <label>Availability (Days)</label>
                    <MultiSelect v-model="formData.affiliation.days" :options="daysOfWeek" optionLabel="name" placeholder="Select available days" display="chip" class="w-half" />
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
                    <FileUpload mode="basic" name="idProof" accept=".pdf" chooseLabel="Choose File" :auto="false" customUpload @select="onSelect($event, 'idProof')" />
                </div>
                <div class="field col-12 md:col-6">
                    <label>Medical License (PDF)</label>
                    <FileUpload mode="basic" name="licenseCert" accept=".pdf" chooseLabel="Choose File" :auto="false" customUpload @select="onSelect($event, 'licenseCert')" />
                </div>
                <div class="field col-12 md:col-6">
                    <label>Qualification Certificates (PDF)</label>
                    <FileUpload mode="basic" name="qualificationCerts" accept=".pdf" chooseLabel="Choose File" :auto="false" customUpload @select="onSelect($event, 'qualificationCerts')" />
                </div>
                <div class="field col-12 md:col-6">
                    <label>Passport Photo</label>
                    <FileUpload mode="basic" name="passportPhoto" accept="image/*" chooseLabel="Choose File" :auto="false" customUpload @select="onSelect($event, 'passportPhoto')" />
                </div>
            </div>
            <div class="text-right">
                <Button label="Back" class="p-button-secondary mr-2" @click="prevStep" />
                <Button label="Next" @click="nextStep" />
            </div>
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
</template>

<style scoped>
.form-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    margin-top: 2rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid #dfe3e8;
    padding-bottom: 0.5rem;
    color: #333;
}

.field {
    margin-bottom: 1.5rem;
}

label {
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: block;
    font-size: 1.1rem;
}

input,
.p-inputtext {
    font-size: 1.05rem;
    padding: 0.75rem;
}

.p-error {
    font-size: 0.85rem;
    color: #d32f2f;
    margin-top: 0.25rem;
    display: block;
}

.text-right {
    text-align: right;
    margin-top: 2rem;
}

button,
.p-button {
    font-size: 1.05rem;
    padding: 0.6rem 1.25rem;
}

.p-button-secondary {
    background-color: #e0e0e0;
    color: #333;
    border: none;
}

.p-button-success {
    background-color: #43a047;
    border: none;
}

.flex.gap-2 {
    gap: 1rem;
}
@media (max-width: 768px) {
    .form-card {
        padding: 1rem !important;
    }

    .section-title {
        font-size: 1.2rem;
    }

    label {
        font-size: 1rem;
    }

    input,
    .p-inputtext {
        font-size: 1rem;
    }

    button,
    .p-button {
        font-size: 1rem;
        padding: 0.5rem 1rem;
    }
}
</style>
