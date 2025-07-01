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
                <StepItem title="Emergency Contacts" />
                <StepItem title="Lifestyle / Habits" />
                <StepItem title="Documents" />
                <StepItem title="Review & Submit" />
            </StepList>
        </Stepper>

        <!-- Step 0: Personal Info -->
        <div v-if="activeStep === 0" class="form-card">
            <p class="section-title">Personal Information</p>
            <div class="grid formgrid">
                <div class="field col-12 md:col-6">
                    <label class="input-label">Full Name</label>
                    <InputText v-model="formData.fullName" :class="{ 'p-invalid': submitted && !formData.fullName }" 
                        class="w-full senior-input" placeholder="Enter your full name" />
                    <small v-if="submitted && !formData.fullName" class="p-error">Full Name is required.</small>
                </div>
                <div class="field col-12 md:col-3">
                    <label class="input-label">Date of Birth</label>
                    <Calendar v-model="formData.dob" class="w-full senior-calendar" showIcon dateFormat="yy-mm-dd" 
                        :class="{ 'p-invalid': submitted && !formData.dob }" />
                    <small v-if="submitted && !formData.dob" class="p-error">DOB is required.</small>
                </div>
                <div class="field col-12 md:col-3">
                    <label class="input-label">Gender</label>
                    <div class="flex flex-wrap gap-3 gender-options">
                        <div class="flex align-items-center" v-for="option in ['Male', 'Female', 'Other']" :key="option">
                            <RadioButton :inputId="option" :value="option" v-model="formData.gender" 
                                class="senior-radio" />
                            <label :for="option" class="ml-2 radio-label">{{ option }}</label>
                        </div>
                    </div>
                    <small v-if="submitted && !formData.gender" class="p-error">Gender is required.</small>
                </div>
            </div>
            <div class="navigation-buttons">
                <Button label="Next" @click="nextStep" class="next-button" />
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
            <div class="navigation-buttons">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Next" @click="nextStep" class="next-button" />
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
            <div class="navigation-buttons">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Next" @click="nextStep" class="next-button" />
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
                    @click="formData.vaccinations.push({ name: '', date: '' })" />
            </div>

            <div class="navigation-buttons">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Next" @click="nextStep" class="next-button" />
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

            <div class="navigation-buttons">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Next" @click="nextStep" class="next-button" />
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
            <div class="navigation-buttons">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Next" @click="nextStep" class="next-button" />
            </div>
        </div>

        <!-- Step 6: Emergency Contacts -->
        <div v-if="activeStep === 6" class="form-card">
            <p class="section-title">Emergency Contacts</p>
            <div v-for="(contact, index) in formData.emergencyContacts" :key="index" class="contact-container grid formgrid mb-4">
                <div class="field col-12 md:col-4">
                    <label class="input-label">Name</label>
                    <InputText v-model="contact.name" class="w-full senior-input" placeholder="Full Name" />
                </div>
                <div class="field col-12 md:col-4">
                    <label class="input-label">Relationship</label>
                    <InputText v-model="contact.relationship" class="w-full senior-input" placeholder="e.g. Son, Daughter" />
                </div>
                <div class="field col-12 md:col-3">
                    <label class="input-label">Contact</label>
                    <InputText v-model="contact.contact" class="w-full senior-input" placeholder="Phone number" />
                </div>
                <div class="field col-12 md:col-1 flex align-items-end">
                    <Button icon="pi pi-trash" severity="danger" class="p-button-sm remove-button" 
                        @click="formData.emergencyContacts.splice(index, 1)" 
                        v-if="formData.emergencyContacts.length > 1" />
                </div>
            </div>
            <Button label="Add Emergency Contact" icon="pi pi-plus" class="p-button-sm mt-2 add-button" 
                @click="formData.emergencyContacts.push({ name: '', relationship: '', contact: '' })" />
            <div class="navigation-buttons mt-3">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Next" @click="nextStep" class="next-button" />
            </div>
        </div>

        <!-- Step 7: Lifestyle / Habits -->
        <div v-if="activeStep === 7" class="form-card">
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

            <div class="navigation-buttons">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Next" @click="nextStep" class="next-button" />
            </div>
        </div>

        <!-- Step 8: Documents -->
        <div v-if="activeStep === 8" class="form-card">
            <p class="section-title">Document Uploads</p>
            <div class="grid formgrid">
                <div class="field col-12 md:col-6">
                    <label class="input-label">ID Proof</label>
                    <FileUpload mode="basic" accept=".pdf,image/*" chooseLabel="Choose File" :auto="false" 
                        customUpload @select="onFileUpload($event, 'idProof')" class="senior-file-upload" />
                    <small v-if="formData.documents.idProof" class="block mt-1 text-sm text-green-600 file-uploaded">
                        {{ formData.documents.idProof }}
                    </small>
                </div>

                <div class="field col-12 md:col-6">
                    <label class="input-label">Medical Report</label>
                    <FileUpload mode="basic" accept=".pdf,image/*" chooseLabel="Choose File" :auto="false" 
                        customUpload @select="onFileUpload($event, 'medicalReport')" class="senior-file-upload" />
                    <small v-if="formData.documents.medicalReport" class="block mt-1 text-sm text-green-600 file-uploaded">
                        {{ formData.documents.medicalReport }}
                    </small>
                </div>

                <div class="field col-12">
                    <label class="input-label">Passport Photo</label>
                    <FileUpload mode="basic" accept="image/*" chooseLabel="Choose File" :auto="false" 
                        customUpload @select="onFileUpload($event, 'passportPhoto')" class="senior-file-upload" />
                    <small v-if="formData.documents.passportPhoto" class="block mt-1 text-sm text-green-600 file-uploaded">
                        {{ formData.documents.passportPhoto }}
                    </small>
                </div>
            </div>

            <div class="navigation-buttons">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Next" @click="nextStep" class="next-button" />
            </div>
        </div>

        <!-- Step 9: Review & Submit -->
        <div v-if="activeStep === 9" class="form-card review-card">
            <p class="section-title">Review & Submit</p>
            <p class="review-text">Please review all your information before submitting. Click submit to complete your registration.</p>
            <div class="navigation-buttons">
                <Button label="Back" class="p-button-secondary mr-2 back-button" @click="prevStep" />
                <Button label="Reset" class="p-button-secondary mr-2 reset-button" @click="resetForm" />
                <Button label="Submit" class="p-button-success submit-button" @click="submitSenior" />
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Calendar from 'primevue/calendar';
import RadioButton from 'primevue/radiobutton';
import Button from 'primevue/button';
import Stepper from 'primevue/stepper';
import StepList from 'primevue/steplist';
import StepItem from 'primevue/stepitem';
import InputGroup from 'primevue/inputgroup';
import FileUpload from 'primevue/fileupload';
import Dropdown from 'primevue/dropdown';

const activeStep = ref(0);
const submitted = ref(false);
const specialityOptions = ['General Physician', 'Cardiologist', 'Endocrinologist', 'Orthopedic', 'Neurologist', 'Psychiatrist', 'Geriatrician', 'Pulmonologist', 'Other'];

const formData = reactive({
    fullName: '',
    dob: '',
    gender: '',
    email: '',
    phone: '',

    medicalConditions: [{ name: '', diagnosedYear: '', curingYear: '', report: '' }],
    medications: [{ name: '', dosage: '', frequency: '', route: '', startDate: '', endDate: '' }],
    vaccinations: [{ name: '', date: '' }],
    insurance: {
        provider: '',
        memberId: '',
        validUpto: '',
        billingContact: ''
    },
    healthcareProvider: {
        Name: '',
        clinic: '',
        contact: '',
        email: '',
        specialty: ''
    },
    emergencyContacts: [{ name: '', relationship: '', contact: '' }],
    lifestyle: {
        smoking: '',
        alcohol: '',
        substanceUse: '',
        diet: '',
        exercise: '',
        livingStatus: '',
        caregiver: ''
    },
    allergies: '',
    documents: {
        idProof: '',
        medicalReport: '',
        passportPhoto: ''
    }
});

onMounted(() => {
    const storedEmail = localStorage.getItem('email');
    if (storedEmail) formData.email = storedEmail;
});

function nextStep() {
    if (activeStep.value < 9) activeStep.value++;
}
function prevStep() {
    if (activeStep.value > 0) activeStep.value--;
}
function addCondition() {
    formData.medicalConditions.push({ name: '', diagnosedYear: '', curingYear: '', report: '' });
}
function addMedication() {
    formData.medications.push({ name: '', dosage: '', frequency: '', route: '', startDate: '', endDate: '' });
}
function onReportUpload(event, index) {
    const file = event.files?.[0];
    if (file) formData.medicalConditions[index].report = file.name;
}
function onFileUpload(event, type) {
    const file = event.files?.[0];
    if (file) {
        formData.documents[type] = file.name;
    }
}

function resetForm() {
    Object.assign(formData, {
        fullName: '',
        dob: '',
        gender: '',
        email: formData.email,
        phone: '',
        medicalConditions: [{ name: '', diagnosedYear: '', curingYear: '', report: '' }],
        medications: [{ name: '', dosage: '', frequency: '', route: '', startDate: '', endDate: '' }],
        vaccinations: [{ name: '', date: '' }],
        insurance: { provider: '', memberId: '', validUpto: '', billingContact: '' },
        healthcareProvider: { Name: '', clinic: '', contact: '', email: '', specialty: '' },
        emergencyContacts: [{ name: '', relationship: '', contact: '' }],
        lifestyle: { smoking: '', alcohol: '', substanceUse: '', diet: '', exercise: '', livingStatus: '', caregiver: '' },
        allergies: '',
        documents: { idProof: '', medicalReport: '', passportPhoto: '' }
    });
    submitted.value = false;
    activeStep.value = 0;
}

function submitSenior() {
    submitted.value = true;
    if (formData.fullName && formData.dob && formData.gender && formData.phone) {
        console.log('Submitted Senior Form Data:', JSON.stringify(formData, null, 2));
        alert('Senior Registration Submitted!');
        resetForm();
    }
}
</script>

<style scoped>
/* Base Styles */
.registration-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
    font-family: 'Arial', sans-serif;
}

.form-title {
    color: #2c3e50;
    text-align: center;
    margin-bottom: 1.5rem;
    font-size: 1.8rem;
    font-weight: 600;
}

.custom-stepper {
    margin-bottom: 2rem;
}

.form-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    margin-top: 1.5rem;
    border: 1px solid #e0e0e0;
}

.section-title {
    font-size: 1.4rem;
    margin-bottom: 1.5rem;
    font-weight: 600;
    color: #3498db;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 0.5rem;
}

.input-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #555;
    font-size: 0.95rem;
}

/* Form Elements */
.senior-input {
    font-size: 1rem;
    padding: 0.75rem;
    border-radius: 8px;
    border: 1px solid #ddd;
    transition: all 0.3s;
}

.senior-input:hover, .senior-input:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.senior-textarea {
    font-size: 1rem;
    padding: 0.75rem;
    border-radius: 8px;
    border: 1px solid #ddd;
    transition: all 0.3s;
    width: 100%;
}

.senior-calendar {
    width: 100%;
}

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