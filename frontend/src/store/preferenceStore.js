import { defineStore } from 'pinia'

export const usePreferenceStore = defineStore('preferenceDetails', {
  state: () => ({
    preset: 'Aura',
    primary: 'emerald',
    surface: 'zinc',
    darkTheme: true,
    menuMode: 'static'
}),

  actions: {
    setPreset(preset) {
        this.preset = preset
    },
    setPrimary(primary) {
        this.primary = primary
    },
    setSurface(surface) {
        this.surface = surface
    },
    setDarktheme() {
        this.darkTheme = !this.darkTheme
    },

    getPreferenceDetails(){
        return {
            preset: this.preset,
            primary: this.primary,
            surface: this.surface,
            darkTheme: this.darkTheme,
            menuMode: this.menuMode,
        }
    }
  },
  persist: true,
})
