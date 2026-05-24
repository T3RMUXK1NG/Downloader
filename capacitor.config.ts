import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.t3rmuxk1ng.downloader',
  appName: 'RS Downloader',
  webDir: 'out',
  bundledWebRuntime: false,
  server: {
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: '#000000',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: true,
      spinnerColor: '#00ff00',
    }
  },
  android: {
    allowMixedContent: true,
    backgroundColor: '#000000',
    buildOptions: {
      keystorePath: 'android/app/release-keystore.jks',
      keystorePassword: '',
      keystoreAlias: 'rs-downloader',
      keystoreAliasPassword: '',
      signingType: 'apksigner'
    }
  }
};

export default config;
