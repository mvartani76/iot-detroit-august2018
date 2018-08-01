//
//  BeaconRangeViewController.swift
//  beacon-scanner
//
//  Created by Michael Vartanian on 7/31/18.
//  Copyright © 2018 Michael Vartanian. All rights reserved.
//

import UIKit
import CoreLocation

class BeaconRangeViewController: UIViewController, CLLocationManagerDelegate {
    
    @IBOutlet var rangeView: UIView!
    @IBOutlet weak var rangeLabel: UILabel!
    
    let IBEACON_PROXIMITY_UUID = "8D847D20-0116-435F-9A21-2FA79A706D9E"
    var locationManager: CLLocationManager!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        locationManager = CLLocationManager()
        locationManager.delegate = self
        locationManager.requestWhenInUseAuthorization()
        locationManager.requestAlwaysAuthorization()
    }
    
    override func viewDidAppear(_ animated: Bool) {
        if let uuid = NSUUID(uuidString: IBEACON_PROXIMITY_UUID) {
            let beaconRegion = CLBeaconRegion(proximityUUID: uuid as UUID, identifier: "iBeacon")
            startRanging(beaconRegion: beaconRegion)
            print("start ranging...")
            rangeLabel.text = ""
            rangeView.backgroundColor = UIColor.white
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        if let uuid = NSUUID(uuidString: IBEACON_PROXIMITY_UUID) {
            let beaconRegion = CLBeaconRegion(proximityUUID: uuid as UUID, identifier: "iBeacon")
            stopRanging(beaconRegion: beaconRegion)
            print("stop ranging...")
        }
    }

    func startRanging(beaconRegion: CLBeaconRegion) {
        locationManager.startRangingBeacons(in: beaconRegion)
    }
    
    func stopRanging(beaconRegion: CLBeaconRegion) {
        locationManager.stopRangingBeacons(in: beaconRegion)
    }
    
    //  ======== CLLocationManagerDelegate methods ==========
    
    func locationManager(_ manager: CLLocationManager, didRangeBeacons beacons: [CLBeacon], in region: CLBeaconRegion) {
        for beacon in beacons {
            var beaconProximity: String;
            switch (beacon.proximity) {
            case .unknown:
                beaconProximity = "Unknown"
                rangeView.backgroundColor = UIColor.white
            case .immediate:
                beaconProximity = "Immediate"
                rangeView.backgroundColor = UIColor.red
            case .near:
                beaconProximity = "Near"
                rangeView.backgroundColor = UIColor.orange
            case .far:
                beaconProximity = "Far"
                rangeView.backgroundColor = UIColor.yellow
            }
            print("BEACON RANGED: uuid: \(beacon.proximityUUID.uuidString) major: \(beacon.major)  minor: \(beacon.minor) proximity: \(beaconProximity)")
            rangeLabel.text = "BEACON RANGED:\nuuid: \(beacon.proximityUUID.uuidString)\nmajor: \(beacon.major)\nminor: \(beacon.minor)\nproximity: \(beaconProximity)\nRSSI: \(beacon.rssi)"
        }
    }
}

