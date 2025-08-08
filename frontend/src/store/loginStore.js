import { defineStore } from 'pinia'

export const useLoginStore = defineStore('loginDetails', {
  state: () => ({
    //basic user details
    ezId: null,
    role: null,
    name: null,
    profileImageUrl: null,

    // senior specific details
    gender: null,
    dob: null,
    address: null,
    pincode: null,
    alternatePhoneNum: null,
    medicalInfo: null,

    // doctor specific details
  }),

  actions: {
    setLoginToken(token){
      localStorage.setItem('EZCARE-LOGIN-TOKEN', token)
    },

    setLoginDetails(details) {
      this.ezId = details.ezId
      this.role = details.role
      this.name = details.name
      this.profileImageUrl = details.profileImageUrl
    },

    setSeniorDetails(details) {
      this.gender = details.gender
      this.dob = details.dob
      this.address = details.address
      this.pincode = details.pincode
      this.alternatePhoneNum = details.alternatePhoneNum
      this.medicalInfo = details.medicalInfo
    },

    setDoctorDetails(details) {
      this.gender = details.gender
      this.dob = details.dob
    },

    clearSeniorDetails() {
      this.gender = null
      this.dob = null
      this.address = null
      this.pincode = null
      this.alternatePhoneNum = null
      this.medicalInfo = null
    },

    clearDoctorDetails() {
      this.gender = null
      this.dob = null
    },

    clearLoginDetails() {
      this.ezId = null
      this.role = null
      this.name = null
      this.profileImageUrl = null
      this.clearSeniorDetails()
      this.clearDoctorDetails()
      localStorage.removeItem('EZCARE-LOGIN-TOKEN')

    },
  },
  persist: true,
})
