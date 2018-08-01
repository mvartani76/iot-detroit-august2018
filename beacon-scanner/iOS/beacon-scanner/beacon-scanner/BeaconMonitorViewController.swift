//
//  BeaconMonitorViewController.swift
//  beacon-scanner
//
//  Created by Michael Vartanian on 7/31/18.
//  Copyright © 2018 Michael Vartanian. All rights reserved.
//

import UIKit
import CoreLocation

class BeaconMonitorViewController: UIViewController, CLLocationManagerDelegate {
    
    let IBEACON_PROXIMITY_UUID = "8D847D20-0116-435F-9A21-2FA79A706D9E"
    var locationManager: CLLocationManager!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        locationManager = CLLocationManager()
        locationManager.delegate = self
        locationManager.requestWhenInUseAuthorization()
        locationManager.requestAlwaysAuthorization()
        print("end of viewdidload")
    }

    override func viewDidAppear(_ animated: Bool) {
        if let uuid = NSUUID(uuidString: IBEACON_PROXIMITY_UUID) {
            print(uuid)
            let beaconRegion = CLBeaconRegion(proximityUUID: uuid as UUID, identifier: "iBeacon")
            startMonitoring(beaconRegion: beaconRegion)
            print("stop monitoring...")
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        if let uuid = NSUUID(uuidString: IBEACON_PROXIMITY_UUID) {
            print(uuid)
            let beaconRegion = CLBeaconRegion(proximityUUID: uuid as UUID, identifier: "iBeacon")
            stopMonitoring(beaconRegion: beaconRegion)
            print("stop monitoring...")
        }
    }
    
    func startMonitoring(beaconRegion: CLBeaconRegion) {
        beaconRegion.notifyOnEntry = true
        beaconRegion.notifyOnExit = true
        locationManager.startMonitoring(for: beaconRegion)
        locationManager.allowsBackgroundLocationUpdates = true
        locationManager.pausesLocationUpdatesAutomatically = false
    }
    
    func stopMonitoring(beaconRegion: CLBeaconRegion) {
        beaconRegion.notifyOnEntry = false
        beaconRegion.notifyOnExit = false
        locationManager.stopMonitoring(for: beaconRegion)
    }
    
    //  ======== CLLocationManagerDelegate methods ==========
    
    func locationManager(_ manager: CLLocationManager, didStartMonitoringFor region: CLRegion) {
        print("monitoring started")
        print(region)
    }
    
    func locationManager(_ manager: CLLocationManager, monitoringDidFailFor region: CLRegion?, withError error: Error) {
        print("monitoring failed")
    }
    
    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        print("i entered a region")
        if let beaconRegion = region as? CLBeaconRegion {
            print("DID ENTER REGION: uuid: \(beaconRegion.proximityUUID.uuidString)")
        }
    }
    
    func locationManager(_ manager: CLLocationManager, didExitRegion region: CLRegion) {
        print("i exited a region")
        if let beaconRegion = region as? CLBeaconRegion {
            print("DID EXIT REGION: uuid: \(beaconRegion.proximityUUID.uuidString)")
        }
    }
/*
    func locationManager(_ manager: CLLocationManager, didDetermineState state: CLRegionState, for region: CLRegion) {
        print("diddeterminestate")
        print(state)
        switch state {
        case .inside:
            print("inside")
        case .outside:
            print("outside")
        case .unknown:
            print("unknown")
        }
    }
    */
}

