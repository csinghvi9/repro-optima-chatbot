// tailwind.config.mjs
export default {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontSize: {
        // Custom font sizes
        'xs-custom': '10px',
        'sm-custom': '12px',
        'base-custom': '14px',
        'lg-custom': '16px',
        'xl-custom': '18px',
      },
      fontFamily: {
        'open-sans': ['"Open Sans"', 'sans-serif'],
      },
      colors: {
        indiraRed: '#F04F5F',
        indiraDarkRed: '#A5273A',
        indiraPink: '#CE3149',
        indiraInputBorder: '#D9D9D9',
        indiraText: '#344054',
        indiraYellow: '#F5FFB4',
        indiraBlue: '#9BEDFF',
      },
    },
  },
  plugins: [],
}
